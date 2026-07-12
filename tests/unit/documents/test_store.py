from divyadrishti.documents import DocumentChunk, InMemoryVectorStore, MockEmbeddingProvider
from divyadrishti.documents.models import ChunkMetadata


def test_in_memory_store_query():
    store = InMemoryVectorStore()
    provider = MockEmbeddingProvider()

    chunks = [
        DocumentChunk(
            text="Jupiter in the 7th house gives a happy marriage.",
            metadata=ChunkMetadata(book_id="BPHS", topics=["marriage"]),
            embedding=provider.embed("marriage jupiter"),
        ),
        DocumentChunk(
            text="Saturn in the 7th house delays marriage.",
            metadata=ChunkMetadata(book_id="BPHS", topics=["marriage"]),
            embedding=provider.embed("saturn delay"),
        ),
    ]
    store.add(chunks)

    results = store.query(provider.embed("marriage jupiter"), n_results=2)
    assert len(results) == 2
    assert results[0].score >= results[1].score


def test_in_memory_store_filter():
    store = InMemoryVectorStore()
    provider = MockEmbeddingProvider()

    chunk = DocumentChunk(
        text="Jupiter in 7th",
        metadata=ChunkMetadata(book_id="BPHS", topics=["marriage"]),
        embedding=provider.embed("jupiter"),
    )
    store.add([chunk])

    results = store.query(provider.embed("jupiter"), filters={"book_id": "BPHS"}, n_results=1)
    assert len(results) == 1

    results = store.query(provider.embed("jupiter"), filters={"book_id": "Other"}, n_results=1)
    assert len(results) == 0
