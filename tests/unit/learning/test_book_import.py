import pytest
from pathlib import Path

from divyadrishti.documents import DocumentProcessingPipeline, InMemoryVectorStore
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import BookImportMonitor
from tests.unit.documents.fake_provider import FakeEmbeddingProvider


@pytest.fixture
def repository(tmp_path):
    return KnowledgeRepository(tmp_path)


@pytest.fixture
def pipeline():
    return DocumentProcessingPipeline(
        embedder=FakeEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
    )


def test_book_import_monitor(tmp_path, repository, pipeline):
    file = tmp_path / "test.txt"
    file.write_text("# Marriage\n\nJupiter in the 7th house indicates a happy marriage.")

    monitor = BookImportMonitor(repository, pipeline)
    report = monitor.process(file, "TEST_BOOK", "Test Book of Astrology")

    assert report.book_id == "TEST_BOOK"
    assert report.chunk_count >= 1
    assert report.candidate_rules
    assert any(f.type == "incomplete_reference" for f in report.findings)
