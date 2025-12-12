#!/usr/bin/env python3
"""
QuizLM - Automated Quiz Generator
Main application entry point
"""

import sys
from pathlib import Path
from ui.main_window import MainWindow


def main() -> int:
    """Main application entry point"""
    try:
        app = MainWindow()
        app.run()
        return 0
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

