"""
Document processing - extract text from various file formats
"""

from pathlib import Path
from typing import Union
import mimetypes

# Import document processing libraries
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from config import Config


class DocumentProcessor:
    """Processes various document formats to extract text content"""

    def __init__(self, config: Config):
        self.config = config

    def process_document(self, file_path: Path) -> str:
        """
        Process a document and extract its text content

        Args:
            file_path: Path to document file

        Returns:
            Extracted text content
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        suffix = file_path.suffix.lower()

        # Process based on file type
        if suffix == '.pdf':
            return self._process_pdf(file_path)
        elif suffix == '.docx':
            return self._process_docx(file_path)
        elif suffix == '.txt':
            return self._process_text(file_path)
        elif suffix in ['.png', '.jpg', '.jpeg']:
            return self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _process_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

        text_parts = []

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text_parts.append(page.extract_text())

        return "\n\n".join(text_parts)

    def _process_docx(self, file_path: Path) -> str:
        """Extract text from Word document"""
        if Document is None:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")

        doc = Document(str(file_path))

        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        return "\n\n".join(text_parts)

    def _process_text(self, file_path: Path) -> str:
        """Read plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _process_image(self, file_path: Path) -> str:
        """Extract text from image using OCR"""
        if Image is None or pytesseract is None:
            raise ImportError(
                "PIL/pytesseract not installed. "
                "Install with: pip install Pillow pytesseract"
            )

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

        return text

