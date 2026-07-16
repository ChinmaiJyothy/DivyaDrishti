"""Embedding providers for document chunks."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base for embedding generation."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for a single text."""

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for multiple texts."""
        return [self.embed(text) for text in texts]


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic mock embedding for tests and local development."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        import hashlib
        import random

        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        return [round(rng.random(), 6) for _ in range(self.dimension)]


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using sentence-transformers.

    Defaults to a multilingual model suitable for Indic and European languages.
    This is the recommended default production embedding provider for the
    Knowledge Corpus, since it runs locally without per-call API cost and
    supports Sanskrit-transliteration and major Indic languages reasonably
    well via its multilingual training data.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self._model: object | None = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ImportError(
                    "sentence-transformers is required for SentenceTransformerEmbeddingProvider. "
                    "Install with: pip install -e \".[ml]\""
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, text: str) -> list[float]:
        model = self._load_model()
        return model.encode(text).tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        return model.encode(texts).tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using OpenAI's embeddings API.

    Requires the ``openai`` package and ``OPENAI_API_KEY`` (or an explicit
    ``api_key``). Useful when a hosted, high-quality embedding model is
    preferred over a local sentence-transformers model.
    """

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._client: object | None = None

    def _load_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise ImportError(
                    "openai is required for OpenAIEmbeddingProvider. "
                    "Install with: pip install -e \".[ai]\""
                ) from exc
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        client = self._load_client()
        response = client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]


def get_embedding_provider(name: str, **kwargs: object) -> EmbeddingProvider:
    """Factory for embedding providers used by the Knowledge Corpus pipeline.

    Production code must never default to ``MockEmbeddingProvider`` — it is
    reserved for unit tests. If an unknown or unavailable provider is
    requested, this raises rather than silently falling back to mock
    embeddings, so ingestion failures are surfaced immediately.
    """
    providers: dict[str, type[EmbeddingProvider]] = {
        "sentence_transformers": SentenceTransformerEmbeddingProvider,
        "openai": OpenAIEmbeddingProvider,
    }
    normalized = name.strip().lower()
    if normalized not in providers:
        raise ValueError(
            f"Unknown embedding provider: {name}. Supported: {sorted(providers)}."
        )
    return providers[normalized](**kwargs)
