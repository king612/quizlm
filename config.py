"""
Configuration management for QuizLM
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

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
        api_key_map = {
            "claude": (self.anthropic_api_key, "ANTHROPIC_API_KEY"),
            "openai": (self.openai_api_key, "OPENAI_API_KEY"),
            "grok": (self.grok_api_key, "GROK_API_KEY"),
        }

        if self.llm_provider in api_key_map:
            api_key, env_var_name = api_key_map[self.llm_provider]
            if not api_key:
                raise ValueError(
                    f"{env_var_name} environment variable not set. "
                    f"Please set it or change QUIZLM_LLM_PROVIDER."
                )

