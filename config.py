"""
Configuration management for QuizLM
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration"""

    def __init__(self):
        # Base directories
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.training_images_dir = self.data_dir / "training_images"
        self.source_documents_dir = self.data_dir / "source_documents"
        self.quizzes_dir = self.data_dir / "quizzes"
        self.models_dir = self.data_dir / "models"

        # Ensure directories exist
        self._create_directories()

        # LLM Configuration
        self.llm_provider = os.getenv("QUIZLM_LLM_PROVIDER", "claude")  # claude, openai, or grok

        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.grok_api_key = os.getenv("GROK_API_KEY")

        # Validate configuration
        self._validate_config()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [
            self.data_dir,
            self.training_images_dir,
            self.source_documents_dir,
            self.quizzes_dir,
            self.models_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _validate_config(self):
        """Validate configuration"""
        # Check that at least one API key is configured
        if self.llm_provider == "claude" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please set it or change QUIZLM_LLM_PROVIDER."
            )
        elif self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it or change QUIZLM_LLM_PROVIDER."
            )
        elif self.llm_provider == "grok" and not self.grok_api_key:
            raise ValueError(
                "GROK_API_KEY environment variable not set. "
                "Please set it or change QUIZLM_LLM_PROVIDER."
            )

