"""
Phase 1: LLM-based word selection for educational value
Asks LLM to identify which words should be blanked based on semantic importance
"""

from typing import List, Dict, Optional
import json

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import httpx
except ImportError:
    httpx = None

from config import Config


class WordSelector:
    """Uses LLM to select educationally valuable words for blanking"""

    def __init__(self, config: Config, proxies: Optional[Dict] = None):
        self.config = config
        self.provider = config.llm_provider
        self.proxies = proxies

        # Create http_client with proxies if needed
        http_client = None
        if proxies:
            if httpx is None:
                raise ImportError("httpx not installed. Install with: pip install httpx")
            http_client = httpx.Client(proxy=proxies)

        # Initialize appropriate client
        if self.provider == "claude":
            if Anthropic is None:
                raise ImportError("anthropic not installed. Install with: pip install anthropic")
            client_kwargs = {"api_key": config.anthropic_api_key}
            if http_client:
                client_kwargs["http_client"] = http_client
            self.client = Anthropic(**client_kwargs)
        elif self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai not installed. Install with: pip install openai")
            client_kwargs = {"api_key": config.openai_api_key}
            if http_client:
                client_kwargs["http_client"] = http_client
            self.client = OpenAI(**client_kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def select_words_to_blank(
        self,
        source_content: str,
        difficulty: str
    ) -> Dict:
        """
        Ask LLM to identify educationally valuable words to blank

        Args:
            source_content: The text to analyze
            difficulty: Easy, Medium, or Hard

        Returns:
            Dictionary with:
                - words_to_blank: List of word objects with word, importance, context
                - difficulty: The difficulty level
                - estimated_coverage: Approximate % of content words selected
        """
        # Validate source content
        if not source_content or not source_content.strip():
            raise ValueError("Source content is empty or invalid")

        # Define target coverage based on difficulty
        target_coverage = {
            "Easy": "15-20% of meaningful content words",
            "Medium": "25-35% of meaningful content words",
            "Hard": "40-50% of meaningful content words"
        }

        prompt = f"""You are an educational content analyzer. Your task is to identify which words in the following text should be tested in a fill-in-the-blank quiz for maximum educational value.

DIFFICULTY LEVEL: {difficulty}
TARGET COVERAGE: {target_coverage[difficulty]}

INSTRUCTIONS:
1. Identify the most educationally valuable words/terms to test
2. Focus on words that test understanding of core concepts
3. Prioritize:
   - Technical terms and specialized vocabulary
   - Key concepts and important nouns
   - Significant verbs and descriptive adjectives
   - Names of people, places, processes, theories
   - Domain-specific terminology
   - Numbers and quantities (when semantically meaningful)

4. AVOID selecting:
   - Articles (a, an, the)
   - Common prepositions (in, on, at, to, from, with, by, for)
   - Common conjunctions (and, but, or, so, yet)
   - Auxiliary verbs (is, are, was, were, have, has, had)
   - Pronouns (it, they, he, she, this, that)
   - Very common words with little semantic value

5. For each word, consider:
   - Is this word central to understanding the content?
   - Does testing this word reinforce key concepts?
   - Would a student need to understand this word to master the material?

Return your analysis as a JSON object with this structure:

{{
  "words_to_blank": [
    {{
      "word": "exact_word_as_it_appears",
      "importance": 0.95,
      "word_type": "key_concept",
      "first_occurrence_context": "brief phrase showing where word first appears"
    }},
    {{
      "word": "another_word",
      "importance": 0.87,
      "word_type": "technical_term",
      "first_occurrence_context": "context snippet"
    }}
  ],
  "difficulty": "{difficulty}",
  "estimated_coverage": 0.25,
  "total_words_selected": 15
}}

IMPORTANT GUIDELINES:
- List words in order of first appearance in the text
- Each word should appear only ONCE in your list (even if it appears multiple times in the text)
- Use the exact spelling and capitalization as it first appears
- For {difficulty} difficulty, aim for roughly {target_coverage[difficulty]}
- word_type can be: key_concept, technical_term, vocabulary, supporting_term, process_name, important_descriptor
- importance score: 0.0 (not important) to 1.0 (critically important)

TEXT TO ANALYZE:
{source_content}

Return ONLY the JSON object, with no explanatory text before or after."""

        # Call LLM
        if self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            content = response.content[0].text
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=3000
            )
            content = response.choices[0].message.content

        # Parse JSON response
        try:
            result = self._extract_json_from_response(content)

            # Validate result structure
            if "words_to_blank" not in result:
                raise ValueError("LLM response missing 'words_to_blank' field")

            # Add metadata
            result["raw_response"] = content
            result["source_length"] = len(source_content)

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content[:500]}")

    def _extract_json_from_response(self, text: str) -> dict:
        """Extract and parse JSON from LLM response text"""
        # Extract JSON if embedded in markdown code block
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        else:
            # Look for JSON object by finding first { and last }
            first_brace = text.find("{")
            last_brace = text.rfind("}")

            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                text = text[first_brace:last_brace + 1].strip()

        return json.loads(text)
