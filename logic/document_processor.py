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

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

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
        """Extract text from PDF file (with OCR fallback for scanned PDFs)"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

        text_parts = []

        try:
            # First, try standard text extraction
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                if len(reader.pages) == 0:
                    raise ValueError("PDF file has no pages")

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()

                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                    else:
                        print(f"Warning: Page {page_num + 1} has no extractable text")

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        # If no text extracted, try OCR fallback
        if not text_parts:
            print("No text found in PDF. Attempting OCR on scanned pages...")
            return self._process_pdf_with_ocr(file_path)

        return "\n\n".join(text_parts)

    def _process_pdf_with_ocr(self, file_path: Path) -> str:
        """Extract text from scanned PDF using OCR"""
        if convert_from_path is None:
            raise ImportError(
                "pdf2image not installed. Install with: pip install pdf2image\n"
                "Note: pdf2image requires poppler:\n"
                "  - macOS: brew install poppler\n"
                "  - Ubuntu/Debian: apt-get install poppler-utils\n"
                "  - Windows: Download from https://github.com/oschwartz10612/poppler-windows"
            )

        if Image is None or pytesseract is None:
            raise ImportError(
                "PIL/pytesseract not installed. "
                "Install with: pip install Pillow pytesseract\n"
                "Note: Tesseract OCR must also be installed:\n"
                "  - macOS: brew install tesseract\n"
                "  - Ubuntu/Debian: apt-get install tesseract-ocr\n"
                "  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )

        text_parts = []

        try:
            print(f"Converting PDF pages to images for OCR...")
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=300)
            print(f"Processing {len(images)} page(s) with OCR...")

            # OCR each page
            for page_num, image in enumerate(images, start=1):
                print(f"  OCR processing page {page_num}...")
                page_text = pytesseract.image_to_string(image)

                if page_text and page_text.strip():
                    text_parts.append(page_text)
                else:
                    print(f"  Warning: No text extracted from page {page_num}")

        except Exception as e:
            raise ValueError(
                f"Failed to OCR PDF. Make sure poppler and tesseract are installed.\n"
                f"Error: {str(e)}"
            )

        if not text_parts:
            raise ValueError(
                "PDF contains no extractable text even with OCR. "
                "The pages may be blank or the image quality may be too poor."
            )

        print(f"OCR completed successfully. Extracted {len(''.join(text_parts))} characters.")
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

