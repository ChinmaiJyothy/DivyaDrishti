import pytest
from pathlib import Path

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import BookImportMonitor


@pytest.fixture
def repository(tmp_path):
    return KnowledgeRepository(tmp_path)


def test_book_import_monitor(tmp_path, repository):
    file = tmp_path / "test.txt"
    file.write_text("# Marriage\n\nJupiter in the 7th house indicates a happy marriage.")

    monitor = BookImportMonitor(repository)
    report = monitor.process(file, "TEST_BOOK", "Test Book of Astrology")

    assert report.book_id == "TEST_BOOK"
    assert report.chunk_count >= 1
    assert report.candidate_rules
    assert any(f.type == "incomplete_reference" for f in report.findings)
