"""
Phase 2: Local deterministic quiz building
Takes word selection from LLM and builds quiz with precise formatting
"""

from typing import List, Dict, Tuple
import re


class QuizBuilder:
    """Builds fill-in-the-blank quizzes with precise formatting control"""

    def __init__(self, difficulty: str = "Medium"):
        """
        Initialize quiz builder

        Args:
            difficulty: Easy, Medium, or Hard (controls hint letter count)
        """
        self.difficulty = difficulty

    def build_quiz(
        self,
        source_text: str,
        words_to_blank: List[Dict],
        max_occurrences_per_word: int = 2
    ) -> Dict:
        """
        Build a quiz from source text and selected words

        Args:
            source_text: The original text content
            words_to_blank: List of word dicts from LLM with 'word', 'importance', etc.
            max_occurrences_per_word: Maximum times to blank each word (default 2)

        Returns:
            Dictionary with:
                - quiz_text: The text with blanks inserted
                - answer_key: List of answer dicts with answer, blank, position
                - metadata: Stats about the quiz
        """
        # Step 1: Collect ALL occurrences across ALL words
        all_occurrences = []

        for word_info in words_to_blank:
            word = word_info.get('word', '')
            if not word:
                continue

            # Find all occurrences of this word in original text
            occurrences = self._find_word_occurrences(source_text, word)

            # Limit to max_occurrences_per_word
            for position, matched_word in occurrences[:max_occurrences_per_word]:
                all_occurrences.append({
                    'position': position,
                    'length': len(matched_word),
                    'matched_word': matched_word,
                    'word_info': word_info,
                    'importance': word_info.get('importance', 0.5)
                })

        # Step 2: Sort by position (DESCENDING - highest position first)
        # This ensures we replace from end to beginning, avoiding position shifts
        all_occurrences.sort(key=lambda x: x['position'], reverse=True)

        # Step 3: Filter out overlapping positions
        # (Check overlaps in the original positions, before any replacements)
        filtered_occurrences = []
        occupied_ranges = []

        for occ in all_occurrences:
            pos = occ['position']
            length = occ['length']
            end_pos = pos + length

            # Check if this position overlaps with any already-selected position
            overlaps = False
            for occupied_start, occupied_end in occupied_ranges:
                if (pos < occupied_end and end_pos > occupied_start):
                    overlaps = True
                    break

            if not overlaps:
                filtered_occurrences.append(occ)
                occupied_ranges.append((pos, end_pos))

        # Step 4: Replace from end to beginning (positions don't shift!)
        quiz_text = source_text
        answer_key = []

        for occ in filtered_occurrences:
            position = occ['position']
            matched_word = occ['matched_word']
            word_info = occ['word_info']

            # Generate the blank with hint letters
            blank = self._generate_blank_with_hint(matched_word)

            # Replace in quiz text (positions are still valid since we work backwards)
            before = quiz_text[:position]
            after = quiz_text[position + len(matched_word):]
            quiz_text = before + blank + after

            # Add to answer key
            answer_key.append({
                "answer": matched_word,
                "blank": blank,
                "position": position,  # Original position in source text
                "importance": word_info.get('importance', 0.5),
                "word_type": word_info.get('word_type', 'unknown')
            })

        # Step 5: Sort answer key by position (ascending) for sequential order
        answer_key.sort(key=lambda x: x['position'])

        # Calculate metadata
        original_word_count = len(source_text.split())
        blanked_word_count = len(answer_key)
        coverage = blanked_word_count / original_word_count if original_word_count > 0 else 0

        return {
            "quiz_text": quiz_text,
            "answer_key": answer_key,
            "metadata": {
                "difficulty": self.difficulty,
                "original_length": len(source_text),
                "quiz_length": len(quiz_text),
                "original_word_count": original_word_count,
                "blanked_word_count": blanked_word_count,
                "coverage_percentage": round(coverage * 100, 1),
                "total_blanks": len(answer_key)
            }
        }

    def _find_word_occurrences(self, text: str, word: str) -> List[Tuple[int, str]]:
        """
        Find all occurrences of a word in text, preserving case and handling punctuation

        Returns:
            List of (position, matched_word) tuples
        """
        occurrences = []

        # Create a pattern that matches the word with word boundaries
        # but captures the actual matched text (preserves case)
        pattern = r'\b' + re.escape(word) + r'\b'

        # Case-insensitive search but preserve original case
        for match in re.finditer(pattern, text, re.IGNORECASE):
            occurrences.append((match.start(), match.group()))

        return occurrences


    def _generate_blank_with_hint(self, word: str) -> str:
        """
        Generate a blank with hint letters based on difficulty

        CRITICAL: Uses EXACTLY 2 underscores per missing letter for handwriting space

        Args:
            word: The word to create a blank for

        Returns:
            String with hint letters + underscores (e.g., "mi__________________________")
        """
        word_length = len(word)

        # Determine hint letter count based on difficulty
        if self.difficulty == "Easy":
            # Show first 40-50% of letters (min 1, max 4)
            hint_count = max(1, min(4, (word_length * 45) // 100))
        elif self.difficulty == "Medium":
            # Show first 25-30% of letters (min 1, max 3)
            hint_count = max(1, min(3, (word_length * 27) // 100))
        else:  # Hard
            # Show first letter only, unless word is very short
            if word_length <= 3:
                hint_count = 1
            elif word_length <= 5:
                hint_count = 1
            else:
                hint_count = 1

        # Extract hint letters (preserve case)
        hint_letters = word[:hint_count]

        # Calculate remaining letters to be blanked
        remaining_letters = word_length - hint_count

        # EXACTLY 2 underscores per missing letter
        underscore_count = remaining_letters * 2

        return hint_letters + ("_" * underscore_count)

    def format_answer_key_for_pdf(self, answer_key: List[Dict]) -> str:
        """
        Format answer key as flowing paragraph with 4-space separation

        Args:
            answer_key: List of answer dictionaries

        Returns:
            Formatted string for PDF rendering
        """
        if not answer_key:
            return "No answers."

        # Extract just the answer words
        answers = [item["answer"] for item in answer_key]

        # Join with 4 spaces
        return "    ".join(answers)

    def create_paragraphs_structure(self, quiz_text: str) -> List[Dict]:
        """
        Convert quiz text into paragraph structure for PDF generation

        Args:
            quiz_text: The complete quiz text with blanks

        Returns:
            List of paragraph dicts with 'text' and optional 'section_heading'
        """
        # Split by double newlines (paragraph boundaries)
        paragraphs = []

        # Split text into chunks (by double newline or similar)
        raw_paragraphs = re.split(r'\n\s*\n', quiz_text)

        for para in raw_paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if this looks like a heading (short, ends with colon, or all caps)
            is_heading = (
                len(para) < 100 and
                (para.endswith(':') or para.isupper() or '\n' not in para)
            )

            if is_heading:
                # Next paragraph will use this as heading
                paragraphs.append({
                    "text": para,
                    "section_heading": None
                })
            else:
                paragraphs.append({
                    "text": para,
                    "section_heading": None
                })

        return paragraphs
