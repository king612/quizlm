"""
PDF generation for quiz sheets
Creates PDF with quiz on left, answers on right
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    canvas = None

from config import Config


class PDFGenerator:
    """Generates PDF quiz sheets with answers"""

    def __init__(self, config: Config):
        self.config = config

        if canvas is None:
            raise ImportError("reportlab not installed. Install with: pip install reportlab")

    def create_quiz_pdf(
        self,
        quiz_data: dict,
        output_path: Path,
        quiz_name: str,
        quiz_style: str = "Split Page"
    ):
        """
        Create a PDF quiz sheet

        Args:
            quiz_data: Quiz content from LLM
            output_path: Where to save PDF
            quiz_name: Name of the quiz
            quiz_style: Layout style ("Split Page" or "Full Page")
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if quiz_style == "Full Page":
            self._create_full_page_quiz(quiz_data, output_path, quiz_name)
        else:
            self._create_split_page_quiz(quiz_data, output_path, quiz_name)

    def _create_split_page_quiz(
        self,
        quiz_data: dict,
        output_path: Path,
        quiz_name: str
    ):
        """Create a split-page quiz (quiz on left, answers on right)"""
        # Create canvas
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Set up fonts
        c.setFont("Helvetica", 11)

        # Margins
        margin = 0.5 * inch
        center_x = width / 2

        # Starting Y position
        y_pos = height - margin

        # Title
        title = quiz_data.get("quiz_title", quiz_name)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_pos, title)
        y_pos -= 30

        # Draw center line
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(center_x, margin, center_x, height - margin)

        # Quiz section label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y_pos, "QUIZ")
        c.drawString(center_x + 10, y_pos, "ANSWERS")
        y_pos -= 20

        # Reset to normal font
        c.setFont("Helvetica", 11)

        # Process paragraphs (new format) or fallback to questions (old format)
        paragraphs = quiz_data.get("paragraphs", [])
        answer_key = quiz_data.get("answer_key", [])

        if not paragraphs:  # Fallback to old question format
            paragraphs = [{"text": q.get("text", ""), "section_heading": None}
                         for q in quiz_data.get("questions", [])]
            answer_key = [{"answer": q.get("answer", ""), "context": ""}
                         for q in quiz_data.get("questions", [])]

        answer_index = 0

        for para in paragraphs:
            # Section heading if present
            if para.get("section_heading"):
                c.setFont("Helvetica-Bold", 12)
                if y_pos < margin + 70:
                    c.showPage()
                    y_pos = height - margin
                    c.setStrokeColor(colors.lightgrey)
                    c.setLineWidth(0.5)
                    c.line(center_x, margin, center_x, height - margin)
                    c.setStrokeColor(colors.black)

                c.drawString(margin, y_pos, para["section_heading"])
                y_pos -= 20
                c.setFont("Helvetica", 11)

            # Word wrap for left side (quiz text)
            left_width = center_x - margin - 15
            quiz_text = para["text"]
            wrapped_quiz = self._wrap_text(quiz_text, left_width, c, 11)

            # Count blanks in this paragraph
            blank_count = quiz_text.count("___")

            # Draw quiz text
            start_y = y_pos
            for line in wrapped_quiz:
                if y_pos < margin + 30:
                    c.showPage()
                    y_pos = height - margin
                    c.setFont("Helvetica", 11)
                    c.setStrokeColor(colors.lightgrey)
                    c.setLineWidth(0.5)
                    c.line(center_x, margin, center_x, height - margin)
                    c.setStrokeColor(colors.black)
                    start_y = y_pos

                c.drawString(margin, y_pos, line)
                y_pos -= 14

            # Draw corresponding answers on right side
            answer_y = start_y
            for _ in range(blank_count):
                if answer_index < len(answer_key):
                    if answer_y < margin + 30:
                        # Continue on next page
                        break
                    answer = answer_key[answer_index]["answer"]
                    c.drawString(center_x + 10, answer_y, answer)
                    answer_y -= 14
                    answer_index += 1

            # Extra space between paragraphs
            y_pos -= 8

        # Footer
        c.setFont("Helvetica", 8)
        footer_text = f"Generated by QuizLM on {datetime.now().strftime('%Y-%m-%d')}"
        c.drawString(margin, margin - 20, footer_text)

        # Save PDF
        c.save()

    def _create_full_page_quiz(
        self,
        quiz_data: dict,
        output_path: Path,
        quiz_name: str
    ):
        """Create a full-page quiz with answers on separate pages at the end"""
        # Create canvas
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Set up fonts
        c.setFont("Helvetica", 11)

        # Margins
        margin = 0.5 * inch
        full_width = width - (2 * margin)

        # Starting Y position
        y_pos = height - margin

        # Title
        title = quiz_data.get("quiz_title", quiz_name)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_pos, title)
        y_pos -= 30

        # Quiz section label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y_pos, "QUIZ")
        y_pos -= 20

        # Reset to normal font
        c.setFont("Helvetica", 11)

        # Process paragraphs (new format) or fallback to questions (old format)
        paragraphs = quiz_data.get("paragraphs", [])
        answer_key = quiz_data.get("answer_key", [])

        if not paragraphs:  # Fallback to old question format
            paragraphs = [{"text": q.get("text", ""), "section_heading": None}
                         for q in quiz_data.get("questions", [])]
            answer_key = [{"answer": q.get("answer", ""), "context": ""}
                         for q in quiz_data.get("questions", [])]

        # Render quiz pages
        for para in paragraphs:
            # Section heading if present
            if para.get("section_heading"):
                c.setFont("Helvetica-Bold", 12)
                if y_pos < margin + 70:
                    c.showPage()
                    y_pos = height - margin

                c.drawString(margin, y_pos, para["section_heading"])
                y_pos -= 20
                c.setFont("Helvetica", 11)

            # Word wrap for full width
            quiz_text = para["text"]
            wrapped_quiz = self._wrap_text(quiz_text, full_width, c, 11)

            # Draw quiz text
            for line in wrapped_quiz:
                if y_pos < margin + 30:
                    c.showPage()
                    y_pos = height - margin
                    c.setFont("Helvetica", 11)

                c.drawString(margin, y_pos, line)
                y_pos -= 14

            # Extra space between paragraphs
            y_pos -= 10

        # Footer on quiz pages
        c.setFont("Helvetica", 8)
        footer_text = f"Generated by QuizLM on {datetime.now().strftime('%Y-%m-%d')}"
        c.drawString(margin, margin - 20, footer_text)

        # Start answer key on new page
        c.showPage()
        y_pos = height - margin

        # Answer key title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_pos, "ANSWER KEY")
        y_pos -= 30

        # Reset to normal font
        c.setFont("Helvetica", 11)

        # Create answer text as flowing paragraphs with 4 spaces between words
        # No numbers, no context - just the words
        answer_words = [ans.get("answer", "") for ans in answer_key]
        answer_paragraph = "    ".join(answer_words)  # 4 spaces between each word

        # Wrap the paragraph to page width
        wrapped_answers = self._wrap_text(answer_paragraph, full_width, c, 11)

        # Render the answer paragraph
        for line in wrapped_answers:
            if y_pos < margin + 30:
                c.showPage()
                y_pos = height - margin
                c.setFont("Helvetica", 11)

            c.drawString(margin, y_pos, line)
            y_pos -= 14

        # Footer on answer page
        c.setFont("Helvetica", 8)
        c.drawString(margin, margin - 20, footer_text)

        # Save PDF
        c.save()

    def _wrap_text(self, text: str, max_width: float, canvas_obj, font_size: int = 11) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = canvas_obj.stringWidth(test_line, "Helvetica", font_size)

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

