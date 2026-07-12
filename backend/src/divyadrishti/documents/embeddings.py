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
                    "sentence-transformers is required for SentenceTransformerEmbeddingProvider."
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, text: str) -> list[float]:
        model = self._load_model()
        return model.encode(text).tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        return model.encode(texts).tolist()
