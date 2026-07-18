import pytest

from divyadrishti.documents.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
    get_default_embedding_provider,
    get_embedding_provider,
)

from .fake_provider import FakeEmbeddingProvider


def test_fake_embedding_deterministic():
    provider = FakeEmbeddingProvider(dimension=384)
    a = provider.embed("Jupiter in the 7th house")
    b = provider.embed("Jupiter in the 7th house")
    assert a == b
    assert len(a) == 384
    assert provider.provider_name == "fake"
    assert provider.model_name == "fake-v1"


def test_fake_embedding_many():
    provider = FakeEmbeddingProvider(dimension=128)
    vectors = provider.embed_many(["text one", "text two"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 128


def test_embedding_provider_interface_requires_embed():
    class BadProvider(EmbeddingProvider):
        provider_name = "bad"
        model_name = "bad-v1"

    with pytest.raises(TypeError):
        BadProvider()


def test_get_embedding_provider_by_name():
    provider = get_embedding_provider("openai", model_name="text-embedding-3-small")
    assert isinstance(provider, OpenAIEmbeddingProvider)
    assert provider.model_name == "text-embedding-3-small"

    provider = get_embedding_provider("sentence_transformers")
    assert isinstance(provider, SentenceTransformerEmbeddingProvider)


def test_get_embedding_provider_unknown_raises():
    with pytest.raises(ValueError):
        get_embedding_provider("unknown_provider")


def test_get_embedding_provider_uses_environment_variable(monkeypatch):
    from divyadrishti.config import get_settings

    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-large")
    get_settings.cache_clear()

    provider = get_embedding_provider()
    assert isinstance(provider, OpenAIEmbeddingProvider)
    assert provider.model_name == "text-embedding-3-large"


def test_openai_provider_reads_api_key_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://test.example.com")
    provider = OpenAIEmbeddingProvider()
    assert provider.api_key == "test-key"
    assert provider.base_url == "https://test.example.com"


def test_get_default_embedding_provider_reads_settings():
    from divyadrishti.config import get_settings

    get_settings.cache_clear()
    provider = get_default_embedding_provider()
    assert provider.provider_name in {"sentence_transformers", "openai"}


def test_openai_provider_retries_api_errors(monkeypatch):
    provider = OpenAIEmbeddingProvider(api_key="test-key")
    calls = {"count": 0}

    def failing_embed_many(texts):
        calls["count"] += 1
        raise ConnectionError("simulated API failure")

    # Replace the provider's embed_many implementation to verify retry logic.
    provider.embed_many = failing_embed_many

    with pytest.raises(ConnectionError):
        provider.embed("hello")

    assert calls["count"] == 3


def test_sentence_transformer_provider_identity():
    provider = SentenceTransformerEmbeddingProvider(model_name="test-model")
    assert provider.provider_name == "sentence_transformers"
    assert provider.model_name == "test-model"
    assert provider.get_metadata() == {
        "provider": "sentence_transformers",
        "model": "test-model",
    }
