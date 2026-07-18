"""Book ingestion pipeline for extracting and storing uploaded book text.

The pipeline accepts PDF uploads (and other supported formats), decides whether
the PDF needs OCR, detects the document language, extracts structural metadata
(chapter, section, verse, page number) and stores the extracted text in the
database. It intentionally does not generate embeddings or candidate rules —
those are downstream steps.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.documents.extractors import ExtractorFactory
from divyadrishti.documents.language import LanguageDetector
from divyadrishti.documents.models import Document
from divyadrishti.knowledge.corpus_pipeline import BookMetadata
from divyadrishti.models import ExtractedBookPage
from divyadrishti.repositories.extracted_book_page import ExtractedBookPageRepository

# Hierarchy extraction patterns
_CHAPTER_PATTERN = re.compile(r"(?i)\b(?:chapter|adhyaya)\s+([0-9]+|[ivxlcdm]+|\w+)\b")
_VERSE_PATTERN = re.compile(r"(?i)\b(?:verse|shloka|sloka|sutra)\s*[:\-]?\s*([0-9]+)\b")
_VERSE_LOCANT_PATTERN = re.compile(r"\b(\d{1,3})\.(\d{1,3})\b")
_HEADING_PATTERN = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)


class BookIngestionReport(BaseModel):
    """Summary of a book text extraction run."""

    book_id: int
    book_title: str
    author: str
    language_detected: str
    ocr_used: bool
    page_count: int
    stored_pages: int
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BookIngestionPipeline:
    """Extract, OCR, and store book text without generating embeddings."""

    def __init__(
        self,
        repository: ExtractedBookPageRepository,
        language_detector: LanguageDetector | None = None,
    ) -> None:
        self.repository = repository
        self.language_detector = language_detector or LanguageDetector()

    def ingest(
        self,
        file_path: Path | str,
        book_id: int,
        metadata: BookMetadata,
    ) -> BookIngestionReport:
        """Run the complete text extraction pipeline for a single book."""
        path = Path(file_path)
        errors: list[str] = []
        warnings: list[str] = []

        if not path.exists():
            raise FileNotFoundError(f"Book file not found: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"Book file is empty: {path}")

        title, author = self._resolve_title_author(path, metadata)

        ocr_used = False
        try:
            extractor, ocr_used = ExtractorFactory.get_extractor_with_ocr_detection(
                path, language_hint=metadata.language_hint
            )
            pages = extractor.extract_pages(path)
        except Exception as exc:
            errors.append(f"Extraction failed: {exc}")
            pages = []

        raw_text = "\n\n".join(text for _, text in pages)
        language = self._detect_language(raw_text, metadata.language_hint, warnings)

        stored_pages = 0
        extracted_pages: list[ExtractedBookPage] = []
        if pages:
            for page_number, page_text in pages:
                hierarchy = self._extract_hierarchy(page_text)
                extracted_pages.append(
                    ExtractedBookPage(
                        book_id=book_id,
                        page_number=page_number,
                        chapter=hierarchy.get("chapter"),
                        section=hierarchy.get("section"),
                        verse=hierarchy.get("verse"),
                        language=language,
                        text=page_text,
                        metadata_json={
                            "title": title,
                            "author": author,
                            "ocr_used": ocr_used,
                            "file_name": path.name,
                        },
                    )
                )
            try:
                self.repository.bulk_create(extracted_pages)
                stored_pages = len(extracted_pages)
            except Exception as exc:
                errors.append(f"Database storage failed: {exc}")

        if not pages:
            warnings.append("No extractable pages found in document.")

        return BookIngestionReport(
            book_id=book_id,
            book_title=title,
            author=author,
            language_detected=language,
            ocr_used=ocr_used,
            page_count=len(pages),
            stored_pages=stored_pages,
            errors=errors,
            warnings=warnings,
        )

    def _resolve_title_author(
        self, path: Path, metadata: BookMetadata
    ) -> tuple[str, str]:
        """Return title and author, falling back to PDF/file metadata."""
        title = metadata.title or ""
        author = metadata.author or ""

        if title and author:
            return title, author

        if path.suffix.lower() == ".pdf":
            pdf_meta = self._extract_pdf_metadata(path)
            title = title or pdf_meta.get("title") or path.stem
            author = author or pdf_meta.get("author") or ""

        title = title or path.stem
        return title, author

    def _extract_pdf_metadata(self, file_path: Path) -> dict[str, str]:
        """Read title/author metadata from a PDF file."""
        metadata: dict[str, str] = {}
        try:
            import fitz
        except ImportError:
            fitz = None  # type: ignore[assignment]

        if fitz:
            try:
                with fitz.open(str(file_path)) as doc:
                    meta = doc.metadata or {}
                    if meta.get("title"):
                        metadata["title"] = str(meta["title"])
                    if meta.get("author"):
                        metadata["author"] = str(meta["author"])
                    return metadata
            except Exception:
                pass

        try:
            from pypdf import PdfReader
        except ImportError:
            return metadata

        try:
            reader = PdfReader(str(file_path))
            meta = reader.metadata or {}
            if meta.title:
                metadata["title"] = str(meta.title)
            if meta.author:
                metadata["author"] = str(meta.author)
        except Exception:
            pass
        return metadata

    def _detect_language(
        self, text: str, language_hint: str | None, warnings: list[str]
    ) -> str:
        """Detect document language, falling back to the supplied hint."""
        if text.strip():
            try:
                return self.language_detector.detect(text)
            except Exception as exc:
                warnings.append(f"Language detection failed: {exc}")
        if language_hint:
            return language_hint
        return "unknown"

    def _extract_hierarchy(self, text: str) -> dict[str, str]:
        """Infer chapter, section, and verse for a page of text."""
        chapter_match = _CHAPTER_PATTERN.search(text)
        chapter = chapter_match.group(1) if chapter_match else ""

        verse_match = _VERSE_PATTERN.search(text)
        if not verse_match:
            locant_match = _VERSE_LOCANT_PATTERN.search(text)
            verse = locant_match.group(2) if locant_match else ""
        else:
            verse = verse_match.group(1)

        section = ""
        heading_match = _HEADING_PATTERN.search(text)
        if heading_match:
            section = heading_match.group(1).lstrip("# ").strip()
        else:
            # Fall back to the first non-empty line if it is short
            first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
            if first_line and len(first_line) < 120:
                section = first_line

        return {"chapter": chapter, "section": section, "verse": verse}
