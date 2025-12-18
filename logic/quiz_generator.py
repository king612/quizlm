"""
Quiz generation logic using 2-phase approach:
Phase 1: LLM selects educationally valuable words
Phase 2: Local code builds quiz with precise formatting
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

from .document_processor import DocumentProcessor
from .word_selector import WordSelector
from .quiz_builder import QuizBuilder
from .pdf_generator import PDFGenerator
from config import Config


class QuizGenerator:
    """Handles quiz generation from source materials"""

    def __init__(self, config: Config, proxies: Optional[Dict] = None):
        self.config = config
        self.doc_processor = DocumentProcessor(config)
        self.word_selector = WordSelector(config, proxies=proxies)
        self.pdf_generator = PDFGenerator(config)

    def generate_quiz(
        self,
        quiz_name: str,
        source_file: Optional[Path] = None,
        source_text: Optional[str] = None,
        difficulty: str = "Medium",
        quiz_style: str = "Split Page"
    ) -> Path:
        """
        Generate a quiz from source material

        Args:
            quiz_name: Unique name for the quiz
            source_file: Path to source document (PDF, DOCX, image, text)
            source_text: Raw text content (alternative to source_file)
            difficulty: Quiz difficulty (Easy, Medium, Hard)
            quiz_style: Quiz layout style (Split Page, Full Page)

        Returns:
            Path to generated PDF quiz
        """
        # Validate inputs
        if not source_file and not source_text:
            raise ValueError("Either source_file or source_text must be provided")

        # Check for duplicate names
        output_path = self.config.quizzes_dir / f"{quiz_name}.pdf"
        if output_path.exists():
            raise ValueError(f"Quiz '{quiz_name}' already exists")

        # Extract content from source
        if source_file:
            content = self.doc_processor.process_document(source_file)
        else:
            content = source_text

        # Validate content
        if not content or not content.strip():
            raise ValueError(
                "Failed to extract content from source document. "
                "The file may be empty, corrupted, or in an unsupported format."
            )

        # Log content length for debugging
        content_length = len(content)
        print(f"Extracted content length: {content_length} characters")
        print(f"First 200 chars: {content[:200]}")

        # Phase 1: LLM selects words to blank based on educational value
        print(f"\n📊 Phase 1: Analyzing content for key terms...")
        word_selection = self.word_selector.select_words_to_blank(
            source_content=content,
            difficulty=difficulty
        )

        num_selected = len(word_selection.get('words_to_blank', []))
        coverage = word_selection.get('estimated_coverage', 0)
        print(f"✓ Selected {num_selected} words to blank (~{coverage*100:.1f}% coverage)")

        # Phase 2: Build quiz locally with precise formatting
        print(f"\n🔧 Phase 2: Building quiz with precise blank formatting...")
        quiz_builder = QuizBuilder(difficulty=difficulty)
        quiz_result = quiz_builder.build_quiz(
            source_text=content,
            words_to_blank=word_selection['words_to_blank'],
            max_occurrences_per_word=2  # Blank each word max 2 times
        )

        metadata = quiz_result['metadata']
        print(f"✓ Created {metadata['total_blanks']} blanks ({metadata['coverage_percentage']}% of words)")

        # Convert to format expected by PDF generator
        quiz_data = {
            "quiz_title": quiz_name,
            "paragraphs": quiz_builder.create_paragraphs_structure(quiz_result['quiz_text']),
            "answer_key": quiz_result['answer_key'],
            "metadata": metadata
        }

        # Generate PDF
        self.pdf_generator.create_quiz_pdf(
            quiz_data=quiz_data,
            output_path=output_path,
            quiz_name=quiz_name,
            quiz_style=quiz_style
        )

        # Save metadata
        self._save_quiz_metadata(quiz_name, quiz_data, difficulty, quiz_style)

        return output_path


    def _save_quiz_metadata(self, quiz_name: str, quiz_data: dict, difficulty: str, quiz_style: str = "Full Page"):
        """Save metadata about generated quiz"""
        metadata_dir = self.config.data_dir / "quiz_metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Extract metadata from quiz_data
        quiz_metadata = quiz_data.get("metadata", {})
        num_items = len(quiz_data.get("paragraphs", []))
        num_blanks = len(quiz_data.get("answer_key", []))

        metadata = {
            "name": quiz_name,
            "difficulty": difficulty,
            "quiz_style": quiz_style,
            "generated_at": datetime.now().isoformat(),
            "num_paragraphs": num_items,
            "num_blanks": num_blanks,
            "version": "3.0",  # New 2-phase architecture
            "generation_method": "llm_selection_local_building",
            "coverage_percentage": quiz_metadata.get("coverage_percentage", 0),
            "original_word_count": quiz_metadata.get("original_word_count", 0)
        }

        metadata_file = metadata_dir / f"{quiz_name}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

