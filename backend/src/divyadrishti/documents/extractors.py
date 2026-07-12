"""Text extractors for PDF, Markdown, TXT, and scanned PDFs."""

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentExtractor(ABC):
    """Abstract base class for extracting text from a document."""

    @abstractmethod
    def extract(self, file_path: Path | str) -> str:
        """Extract text from the file and return the raw text."""


class PDFExtractor(DocumentExtractor):
    """Extract text from PDFs using PyMuPDF or pypdf.

    PyMuPDF is preferred because it can extract text from OCR-layered PDFs
    and from documents containing images and mixed languages.
    """

    def extract(self, file_path: Path | str) -> str:
        path = str(file_path)

        try:
            import fitz
        except ImportError:
            fitz = None

        if fitz:
            return self._extract_with_fitz(path)

        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError("pypdf or pymupdf is required for PDF extraction.") from exc

        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _extract_with_fitz(self, file_path: str) -> str:
        import fitz

        doc = fitz.open(file_path)
        pages = []
        for page in doc:
            text = page.get_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)


class ScannedPDFExtractor(DocumentExtractor):
    """Extract text from scanned PDFs using OCR.

    Requires pytesseract and pdf2image to be installed, plus the Tesseract binary.
    """

    def __init__(self, language: str = "eng") -> None:
        self.language = language

    def extract(self, file_path: Path | str) -> str:
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError as exc:
            raise ImportError(
                "pytesseract and pdf2image are required for OCR."
            ) from exc

        images = convert_from_path(str(file_path))
        texts = []
        for image in images:
            text = pytesseract.image_to_string(image, lang=self.language)
            if text:
                texts.append(text)
        return "\n\n".join(texts)


class MarkdownExtractor(DocumentExtractor):
    """Extract text from Markdown files."""

    def extract(self, file_path: Path | str) -> str:
        return Path(file_path).read_text(encoding="utf-8")


class TextExtractor(DocumentExtractor):
    """Extract text from plain text files."""

    def extract(self, file_path: Path | str) -> str:
        return Path(file_path).read_text(encoding="utf-8")


class ExtractorFactory:
    """Factory to select the right extractor for a file type."""

    @staticmethod
    def get_extractor(file_path: Path | str, ocr_enabled: bool = False) -> DocumentExtractor:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            if ocr_enabled:
                return ScannedPDFExtractor()
            return PDFExtractor()
        if suffix in {".md", ".markdown"}:
            return MarkdownExtractor()
        if suffix == ".txt":
            return TextExtractor()

        raise ValueError(f"Unsupported file type: {suffix}")
