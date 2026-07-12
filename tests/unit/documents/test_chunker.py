from divyadrishti.documents import SemanticChunker
from divyadrishti.documents.models import Document


def test_chunker_splits_by_heading():
    text = """
# Chapter 1

This is the first paragraph of chapter one.

This is the second paragraph.

## Section 1.1

Section text here.
"""
    doc = Document(source_path="test.md", file_type=".md", raw_text=text)
    chunker = SemanticChunker(max_chunk_size=200)
    chunks = chunker.chunk(doc, book_id="BPHS", book_title="Test Book")

    assert len(chunks) >= 2
    assert chunks[0].metadata.book_id == "BPHS"
    assert "Chapter 1" in chunks[0].metadata.section or "Chapter 1" in chunks[0].text


def test_chunker_max_size():
    text = "\n\n".join(["Paragraph " + str(i) for i in range(50)])
    doc = Document(source_path="test.txt", file_type=".txt", raw_text=text)
    chunker = SemanticChunker(max_chunk_size=300, overlap=20)
    chunks = chunker.chunk(doc, book_id="BPHS")

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 350
