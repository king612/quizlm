"""
Quiz generation logic using LLM-based approach
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

from .document_processor import DocumentProcessor
from .llm_client import LLMClient
from .pdf_generator import PDFGenerator
from config import Config


class QuizGenerator:
    """Handles quiz generation from source materials"""

    def __init__(self, config: Config, proxies: Optional[Dict] = None):
        self.config = config
        self.doc_processor = DocumentProcessor(config)
        self.llm_client = LLMClient(config, proxies=proxies)
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

        # Warn about size limits (Claude Haiku has 4K output limit)
        if content_length > 10000:
            print(f"\n⚠️  WARNING: Large document detected ({content_length} chars)")
            print(f"   Claude Haiku's 4K output limit may truncate the quiz.")
            print(f"   Recommended: Use documents under 8000 characters (~3-4 pages)")
            print(f"   Or split into multiple smaller documents.\n")

        # Load style information from training
        style_info = self._load_style_info()

        # Generate quiz content using LLM
        quiz_data = self.llm_client.generate_quiz_content(
            source_content=content,
            difficulty=difficulty,
            style_info=style_info
        )

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

    def _load_style_info(self) -> dict:
        """Load style information from training data"""
        style_file = self.config.models_dir / "style_info.json"

        if not style_file.exists():
            # Return default style if no training done yet
            return {
                "format": "two-column",
                "font": "Verdana",
                "font_size": 12,
                "hint_patterns": {
                    "Easy": "first_1-2_letters",
                    "Medium": "first_letter_occasional",
                    "Hard": "no_hints_mostly"
                }
            }

        with open(style_file, 'r') as f:
            return json.load(f)

    def _save_quiz_metadata(self, quiz_name: str, quiz_data: dict, difficulty: str, quiz_style: str = "Full Page"):
        """Save metadata about generated quiz"""
        metadata_dir = self.config.data_dir / "quiz_metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Support both old (questions) and new (paragraphs) formats
        num_items = len(quiz_data.get("paragraphs", quiz_data.get("questions", [])))
        num_blanks = len(quiz_data.get("answer_key", quiz_data.get("questions", [])))

        metadata = {
            "name": quiz_name,
            "difficulty": difficulty,
            "quiz_style": quiz_style,
            "generated_at": datetime.now().isoformat(),
            "num_paragraphs": num_items,
            "num_blanks": num_blanks,
        }

        metadata_file = metadata_dir / f"{quiz_name}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

