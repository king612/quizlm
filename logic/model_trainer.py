"""
Model training logic - analyzes handwritten quiz images to extract style
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil
from datetime import datetime
import tempfile

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

from .llm_client import LLMClient
from config import Config


class ModelTrainer:
    """Handles training/analysis of quiz style from handwritten examples"""

    def __init__(self, config: Config, proxies: Optional[Dict] = None):
        self.config = config
        self.llm_client = LLMClient(config, proxies=proxies)

    def add_training_image(self, image_path: Path, name: str):
        """
        Add a new training image

        Args:
            image_path: Path to the image file
            name: Unique name for this training image
        """
        # Check for duplicates
        training_images_dir = self.config.training_images_dir
        training_images_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize name
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))
        suffix = image_path.suffix
        target_path = training_images_dir / f"{safe_name}{suffix}"

        if target_path.exists():
            raise ValueError(f"Training image '{name}' already exists")

        # Copy image to training directory
        shutil.copy2(image_path, target_path)

    def get_training_images(self) -> List[Path]:
        """Get list of all training images and PDFs"""
        training_images_dir = self.config.training_images_dir

        if not training_images_dir.exists():
            return []

        # Get all image files and PDFs
        images = [
            img for ext in ['.png', '.jpg', '.jpeg', '.pdf']
            for img in training_images_dir.glob(f"*{ext}")
        ]
        return sorted(images)

    def train_model(self):
        """
        Analyze training images to extract style information
        Uses vision LLM to understand the quiz format and style
        Supports both image files and PDFs (each page analyzed separately)
        """
        training_files = self.get_training_images()

        if not training_files:
            raise ValueError("No training images available. Add some training images first.")

        # Backup existing model if it exists
        self._backup_existing_model()

        # Analyze each training image/PDF with vision LLM
        style_analyses = []
        for file_path in training_files:
            if file_path.suffix.lower() == '.pdf':
                # Handle PDF: convert each page to image and analyze
                pdf_analyses = self._analyze_pdf_pages(file_path)
                style_analyses.extend(pdf_analyses)
            else:
                # Handle regular image
                analysis = self.llm_client.analyze_quiz_image(file_path)
                style_analyses.append(analysis)

        # Aggregate style information
        aggregated_style = self._aggregate_style_info(style_analyses)

        # Save style information
        self._save_style_info(aggregated_style)

    def _analyze_pdf_pages(self, pdf_path: Path) -> List[dict]:
        """
        Convert PDF pages to images and analyze each page

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of analyses, one per page
        """
        if convert_from_path is None:
            raise ImportError(
                "pdf2image not installed. Install with: pip install pdf2image\n"
                "Note: pdf2image also requires poppler to be installed:\n"
                "  - macOS: brew install poppler\n"
                "  - Ubuntu/Debian: apt-get install poppler-utils\n"
                "  - Windows: Download from https://github.com/oschwartz10612/poppler-windows"
            )

        analyses = []

        # Create temporary directory for page images
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Convert PDF pages to images
            try:
                images = convert_from_path(pdf_path, dpi=200)
            except Exception as e:
                raise ValueError(
                    f"Failed to convert PDF to images. Make sure poppler is installed.\n"
                    f"Error: {str(e)}"
                )

            # Save and analyze each page
            for page_num, image in enumerate(images, start=1):
                # Save page as temporary PNG
                page_image_path = temp_path / f"page_{page_num}.png"
                image.save(page_image_path, 'PNG')

                # Analyze the page
                try:
                    analysis = self.llm_client.analyze_quiz_image(page_image_path)
                    # Add metadata about source
                    analysis['source_file'] = pdf_path.name
                    analysis['page_number'] = page_num
                    analyses.append(analysis)
                except Exception as e:
                    print(f"Warning: Failed to analyze page {page_num} of {pdf_path.name}: {e}")
                    continue

        return analyses

    def _backup_existing_model(self):
        """Backup the current model (style info) if it exists"""
        style_file = self.config.models_dir / "style_info.json"

        if style_file.exists():
            backup_dir = self.config.models_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"style_info_backup_{timestamp}.json"

            shutil.copy2(style_file, backup_path)

    def _aggregate_style_info(self, analyses: List[dict]) -> dict:
        """Aggregate style information from multiple analyses"""
        # This combines insights from all training images
        # For now, we'll use the most common patterns

        aggregated = {
            "format": "two-column",  # Most common format
            "font": "Verdana",
            "font_size": 12,
            "hint_patterns": {
                "Easy": "first_1-2_letters",
                "Medium": "first_letter_occasional",
                "Hard": "no_hints_mostly"
            },
            "training_images_analyzed": len(analyses),
            "raw_analyses": analyses  # Keep individual analyses for reference
        }

        return aggregated

    def _save_style_info(self, style_info: dict):
        """Save aggregated style information"""
        self.config.models_dir.mkdir(parents=True, exist_ok=True)

        style_file = self.config.models_dir / "style_info.json"
        with open(style_file, 'w') as f:
            json.dump(style_info, f, indent=2)

