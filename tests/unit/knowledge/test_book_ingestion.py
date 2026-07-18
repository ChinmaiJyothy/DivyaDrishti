"""Tests for the BookIngestionPipeline."""

from pathlib import Path

import pytest
import fitz

from divyadrishti.knowledge.book_ingestion import BookIngestionPipeline, BookIngestionReport
from divyadrishti.knowledge.corpus_pipeline import BookMetadata
from divyadrishti.models import ExtractedBookPage
from divyadrishti.repositories.extracted_book_page import ExtractedBookPageRepository


class FakeExtractedBookPageRepository:
    """In-memory stand-in for the extracted page repository."""

    def __init__(self) -> None:
        self.pages: list[ExtractedBookPage] = []
        self._next_id = 1

    def bulk_create(self, pages: list[ExtractedBookPage]) -> list[ExtractedBookPage]:
        for page in pages:
            page.id = self._next_id
            self._next_id += 1
            self.pages.append(page)
        return pages

    def list_by_book(self, book_id: int) -> list[ExtractedBookPage]:
        return [p for p in self.pages if p.book_id == book_id]


def test_pipeline_ingests_text_file_with_hierarchy(tmp_path: Path) -> None:
    book_file = tmp_path / "sample.txt"
    book_file.write_text(
        "Chapter 1\n\nVerse 1: The king who follows dharma prospers.\n\n"
        "Verse 2: Wealth follows virtue.\n\n## Section 2\n\nVerse 3: Planets reveal destiny.\n"
    )

    repo = FakeExtractedBookPageRepository()
    pipeline = BookIngestionPipeline(repository=repo)
    metadata = BookMetadata(title="Test Book", author="Tester", language_hint="en")

    report = pipeline.ingest(book_file, book_id=7, metadata=metadata)

    assert isinstance(report, BookIngestionReport)
    assert report.book_id == 7
    assert report.book_title == "Test Book"
    assert report.author == "Tester"
    assert report.page_count == 1
    assert report.stored_pages == 1
    assert not report.ocr_used
    assert report.language_detected != "unknown"
    assert not report.errors

    assert len(repo.pages) == 1
    page = repo.pages[0]
    assert page.book_id == 7
    assert page.page_number == 1
    assert page.chapter == "1"
    assert page.verse in ("1", "2", "3")
    assert page.text


def test_pipeline_extracts_pdf_metadata_and_hierarchy(tmp_path: Path) -> None:
    book_file = tmp_path / "sample.pdf"
    doc = fitz.open()
    doc.set_metadata({"title": "PDF Book", "author": "PDF Author"})
    page = doc.new_page()
    page.insert_text((72, 72), "Chapter 2\n\nVerse 1: Sample text for a digital PDF.")
    doc.save(str(book_file))
    doc.close()

    repo = FakeExtractedBookPageRepository()
    pipeline = BookIngestionPipeline(repository=repo)
    metadata = BookMetadata(title="", author="")

    report = pipeline.ingest(book_file, book_id=5, metadata=metadata)

    assert report.book_title == "PDF Book"
    assert report.author == "PDF Author"
    assert report.page_count == 1
    assert report.stored_pages == 1
    assert not report.ocr_used

    page = repo.pages[0]
    assert page.chapter == "2"
    assert page.verse == "1"
    assert "Sample text" in page.text


def test_pipeline_detects_scanned_pdf_and_flags_ocr(tmp_path: Path) -> None:
    """A blank PDF has no text, so the pipeline should choose OCR and store nothing."""
    book_file = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(book_file))
    doc.close()

    repo = FakeExtractedBookPageRepository()
    pipeline = BookIngestionPipeline(repository=repo)
    metadata = BookMetadata(title="Blank")

    # OCR requires pytesseract/pdf2image, which will not be installed in most test runs.
    # The pipeline should record the error and return a report rather than crash.
    report = pipeline.ingest(book_file, book_id=6, metadata=metadata)

    assert report.book_id == 6
    assert report.ocr_used
    assert report.page_count == 0
    assert report.stored_pages == 0
    assert report.errors
    assert len(repo.pages) == 0


def test_pipeline_falls_back_to_filename_for_title(tmp_path: Path) -> None:
    book_file = tmp_path / "my_awesome_book.txt"
    book_file.write_text("Some plain text without any headings.")

    repo = FakeExtractedBookPageRepository()
    pipeline = BookIngestionPipeline(repository=repo)
    metadata = BookMetadata(title="", author="")

    report = pipeline.ingest(book_file, book_id=8, metadata=metadata)

    assert report.book_title == "my_awesome_book"
    assert report.author == ""
    assert report.stored_pages == 1
