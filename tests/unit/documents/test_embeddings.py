from divyadrishti.documents import MockEmbeddingProvider


def test_mock_embedding_deterministic():
    provider = MockEmbeddingProvider(dimension=384)
    a = provider.embed("Jupiter in the 7th house")
    b = provider.embed("Jupiter in the 7th house")
    assert a == b
    assert len(a) == 384


def test_mock_embedding_many():
    provider = MockEmbeddingProvider(dimension=128)
    vectors = provider.embed_many(["text one", "text two"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 128
