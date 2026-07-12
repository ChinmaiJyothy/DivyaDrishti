from divyadrishti.documents import ChunkMetadata, Document, DocumentChunk


def test_chunk_metadata_citation():
    meta = ChunkMetadata(
        book_id="BPHS",
        book_title="Brihat Parashara Hora Shastra",
        chapter="7",
        verse="12",
        page_number=45,
        chunk_index=3,
    )
    chunk = DocumentChunk(text="sample", metadata=meta)
    assert "Brihat Parashara Hora Shastra" in chunk.build_citation()
    assert "Verse 12" in chunk.build_citation()


def test_document_total_chunks():
    doc = Document(source_path="book.md", file_type=".md")
    chunk = DocumentChunk(text="sample", metadata=ChunkMetadata(book_id="BPHS"))
    doc.chunks.append(chunk)
    assert doc.total_chunks() == 1
