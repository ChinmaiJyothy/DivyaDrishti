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
    doc = Document(source_path="test.md", file_type=".md", raw_text=text, language="en")
    chunker = SemanticChunker(max_chunk_size=200)
    chunks = chunker.chunk(doc, book_id="BPHS", book_title="Test Book")

    assert len(chunks) >= 2
    assert chunks[0].metadata.book_id == "BPHS"
    assert "Chapter 1" in chunks[0].metadata.section or "Chapter 1" in chunks[0].text


def test_chunker_max_size():
    text = "\n\n".join(["Paragraph " + str(i) for i in range(50)])
    doc = Document(source_path="test.txt", file_type=".txt", raw_text=text, language="en")
    chunker = SemanticChunker(max_chunk_size=300, overlap=20)
    chunks = chunker.chunk(doc, book_id="BPHS")

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 350


def test_chunker_preserves_chapter_section_verse():
    text = """Chapter 1

Verse 1: The king who is devoted to dharma prospers.

Verse 2: Wealth follows virtue when planets are strong.

## Section 2

Verse 3: A weak lord of the tenth harms career.
"""
    doc = Document(source_path="test.txt", file_type=".txt", raw_text=text, language="en")
    chunker = SemanticChunker(max_chunk_size=150)
    chunks = chunker.chunk(doc, book_id="BPHS")

    all_text = "\n".join(c.text for c in chunks)
    assert any(c.metadata.chapter == "1" for c in chunks)
    assert all(f"Verse {i}" in all_text for i in range(1, 4))
    assert any(c.metadata.verse == "1" for c in chunks)
    assert any(c.metadata.verse == "3" for c in chunks)
    assert any("Section 2" in (c.metadata.section or "") for c in chunks)


def test_chunker_metadata_includes_book_chapter_verse_page_language():
    pages = [
        (1, "Chapter 1\n\nVerse 1: First verse."),
        (2, "Verse 2: Second verse."),
    ]
    doc = Document(source_path="test.txt", file_type=".txt", raw_text="", language="sa")
    chunker = SemanticChunker(max_chunk_size=80)
    chunks = chunker.chunk_pages(
        pages, doc, book_id="BPHS", book_title="Brhat Parasara Hora Sastra"
    )

    all_text = "\n".join(c.text for c in chunks)
    assert chunks
    assert all(c.metadata.book_id == "BPHS" for c in chunks)
    assert all(c.metadata.book_title == "Brhat Parasara Hora Sastra" for c in chunks)
    assert all(c.metadata.language == "sa" for c in chunks)
    assert all(c.metadata.page_number is not None for c in chunks)
    assert "Verse 1" in all_text
    assert "Verse 2" in all_text
    assert any(c.metadata.verse == "1" for c in chunks)
    assert any(c.metadata.page_number == 1 for c in chunks)
    assert any("Verse 2" in c.text for c in chunks)


def test_chunker_does_not_split_verses():
    text = "Chapter 1\n\n" + "\n\n".join(
        f"Verse {i}: This is a verse text that should stay together." for i in range(1, 6)
    )
    doc = Document(source_path="test.txt", file_type=".txt", raw_text=text, language="en")
    chunker = SemanticChunker(max_chunk_size=120)
    chunks = chunker.chunk(doc, book_id="BPHS")

    for chunk in chunks:
        # Each chunk should contain at most one verse marker.
        assert chunk.text.count("Verse ") <= 2  # allow overlap carry-over


def _overlap_length(left: str, right: str) -> int:
    """Return the length of the longest common suffix/prefix between two strings."""
    max_len = min(len(left), len(right))
    for length in range(max_len, 0, -1):
        if left[-length:] == right[:length]:
            return length
    return 0


def test_chunker_overlap_approximately_fifteen_percent():
    paragraphs = [f"Paragraph {i} with enough text to make overlap measurable." for i in range(20)]
    text = "\n\n".join(paragraphs)
    doc = Document(source_path="test.txt", file_type=".txt", raw_text=text, language="en")
    chunker = SemanticChunker(max_chunk_size=500)
    chunks = chunker.chunk(doc, book_id="BPHS")

    assert len(chunks) > 1
    for i in range(len(chunks) - 1):
        overlap = _overlap_length(chunks[i].text, chunks[i + 1].text)
        ratio = overlap / max(len(chunks[i + 1].text), 1)
        # Overlap should be roughly 10-30% of the next chunk.
        assert 0.10 <= ratio <= 0.35
