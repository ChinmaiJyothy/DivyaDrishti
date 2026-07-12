import pytest
from pathlib import Path

from divyadrishti.documents import (
    DocumentProcessingPipeline,
    InMemoryVectorStore,
    MockEmbeddingProvider,
    DocumentRetrievalEngine,
)


@pytest.fixture
def pipeline():
    return DocumentProcessingPipeline(
        embedder=MockEmbeddingProvider(),
        vector_store=InMemoryVectorStore(),
    )


def test_process_text(tmp_path, pipeline):
    file = tmp_path / "test.txt"
    file.write_text("# Chapter 1\n\nJupiter in the 7th house gives a happy marriage.", encoding="utf-8")
    result = pipeline.process(file, book_id="BPHS", book_title="Test Book")

    assert result.chunk_count >= 1
    assert result.stored is True
    assert result.language == "en"


def test_process_directory(tmp_path, pipeline):
    (tmp_path / "a.txt").write_text("Jupiter in 7th.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Saturn in 7th.", encoding="utf-8")

    results = pipeline.process_directory(tmp_path)
    assert len(results) == 2
    assert all(r.stored for r in results)


def test_retrieval_after_pipeline(tmp_path, pipeline):
    file = tmp_path / "test.txt"
    file.write_text("Jupiter in the 7th house brings harmony.", encoding="utf-8")
    pipeline.process(file, book_id="BPHS", book_title="Test Book")

    engine = DocumentRetrievalEngine(pipeline.vector_store, pipeline.embedder)
    results = engine.semantic_search("Jupiter 7th marriage", n_results=3)
    assert len(results) >= 1
