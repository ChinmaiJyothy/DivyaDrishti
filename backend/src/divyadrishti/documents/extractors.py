"""Text extractors for PDF, Markdown, TXT, and scanned PDFs."""

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentExtractor(ABC):
    """Abstract base class for extracting text from a document."""

    @abstractmethod
    def extract(self, file_path: Path | str) -> str:
        """Extract text from the file and return the raw text."""

    def extract_pages(self, file_path: Path | str) -> list[tuple[int, str]]:
        """Extract text per page as ``(page_number, text)`` tuples.

        Default implementation treats the whole document as a single page.
        Extractors that have real page boundaries (PDFs) override this.
        """
        return [(1, self.extract(file_path))]


# A page whose average character count falls below this threshold is
# considered "scanned" (i.e. the digital text layer is missing or corrupt)
# and should be retried with OCR.
MIN_CHARS_PER_PAGE_THRESHOLD = 20


class PDFExtractor(DocumentExtractor):
    """Extract text from PDFs using PyMuPDF or pypdf.

    PyMuPDF is preferred because it can extract text from OCR-layered PDFs
    and from documents containing images and mixed languages.
    """

    def extract(self, file_path: Path | str) -> str:
        pages = self.extract_pages(file_path)
        return "\n\n".join(text for _, text in pages)

    def extract_pages(self, file_path: Path | str) -> list[tuple[int, str]]:
        path = str(file_path)

        try:
            import fitz
        except ImportError:
            fitz = None

        if fitz:
            return self._extract_pages_with_fitz(path)

        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError("pypdf or pymupdf is required for PDF extraction.") from exc

        reader = PdfReader(path)
        pages: list[tuple[int, str]] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append((index, text))
        return pages

    def _extract_pages_with_fitz(self, file_path: str) -> list[tuple[int, str]]:
        import fitz

        doc = fitz.open(file_path)
        pages: list[tuple[int, str]] = []
        for index, page in enumerate(doc, start=1):
            text = page.get_text() or ""
            pages.append((index, text))
        return pages

    def needs_ocr(self, file_path: Path | str) -> bool:
        """Return True if the extracted text is too sparse, indicating a scanned PDF."""
        pages = self.extract_pages(file_path)
        if not pages:
            return True
        total_chars = sum(len(text.strip()) for _, text in pages)
        avg_chars = total_chars / len(pages)
        return avg_chars < MIN_CHARS_PER_PAGE_THRESHOLD


class ScannedPDFExtractor(DocumentExtractor):
    """Extract text from scanned PDFs using OCR.

    Requires pytesseract and pdf2image to be installed, plus the Tesseract binary.
    """

    # Maps ISO 639-1-ish language hints to Tesseract language codes.
    TESSERACT_LANGUAGE_MAP = {
        "en": "eng",
        "sa": "san",
        "hi": "hin",
        "kn": "kan",
        "te": "tel",
        "ta": "tam",
        "ml": "mal",
        "gu": "guj",
        "mr": "mar",
    }

    def __init__(self, language: str = "eng") -> None:
        self.language = language

    @classmethod
    def for_language_hint(cls, language_hint: str | None) -> "ScannedPDFExtractor":
        """Build an extractor using the best-matching Tesseract language code."""
        tess_lang = cls.TESSERACT_LANGUAGE_MAP.get((language_hint or "en").lower(), "eng")
        return cls(language=tess_lang)

    def extract(self, file_path: Path | str) -> str:
        pages = self.extract_pages(file_path)
        return "\n\n".join(text for _, text in pages)

    def extract_pages(self, file_path: Path | str) -> list[tuple[int, str]]:
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError as exc:
            raise ImportError(
                "pytesseract and pdf2image are required for OCR."
            ) from exc

        images = convert_from_path(str(file_path))
        pages: list[tuple[int, str]] = []
        for index, image in enumerate(images, start=1):
            text = pytesseract.image_to_string(image, lang=self.language) or ""
            pages.append((index, text))
        return pages


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

    @staticmethod
    def get_extractor_with_ocr_detection(
        file_path: Path | str, language_hint: str | None = None
    ) -> tuple[DocumentExtractor, bool]:
        """Select an extractor and auto-detect whether OCR is required.

        For PDFs, the digital text layer is inspected first; if it is too
        sparse (scanned pages with no embedded text), a
        ``ScannedPDFExtractor`` tuned to the book's language hint is
        returned instead. Returns ``(extractor, ocr_used)``.
        """
        path = Path(file_path)
        if path.suffix.lower() != ".pdf":
            return ExtractorFactory.get_extractor(path), False

        pdf_extractor = PDFExtractor()
        try:
            if pdf_extractor.needs_ocr(path):
                return ScannedPDFExtractor.for_language_hint(language_hint), True
        except Exception:
            # If page inspection fails for any reason, fall back to OCR
            # rather than silently returning an empty document.
            return ScannedPDFExtractor.for_language_hint(language_hint), True
        return pdf_extractor, False
