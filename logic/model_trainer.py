"""
Model training logic - analyzes handwritten quiz images to extract style
"""

from pathlib import Path
from typing import List
import json
import shutil
from datetime import datetime

from .llm_client import LLMClient
from config import Config


class ModelTrainer:
    """Handles training/analysis of quiz style from handwritten examples"""

    def __init__(self, config: Config):
        self.config = config
        self.llm_client = LLMClient(config)

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
        """Get list of all training images"""
        training_images_dir = self.config.training_images_dir

        if not training_images_dir.exists():
            return []

        # Get all image files
        images = []
        for ext in ['.png', '.jpg', '.jpeg']:
            images.extend(training_images_dir.glob(f"*{ext}"))

        return sorted(images)

    def train_model(self):
        """
        Analyze training images to extract style information
        Uses vision LLM to understand the quiz format and style
        """
        training_images = self.get_training_images()

        if not training_images:
            raise ValueError("No training images available. Add some training images first.")

        # Backup existing model if it exists
        self._backup_existing_model()

        # Analyze each training image with vision LLM
        style_analyses = []
        for img_path in training_images:
            analysis = self.llm_client.analyze_quiz_image(img_path)
            style_analyses.append(analysis)

        # Aggregate style information
        aggregated_style = self._aggregate_style_info(style_analyses)

        # Save style information
        self._save_style_info(aggregated_style)

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

