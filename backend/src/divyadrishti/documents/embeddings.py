"""Embedding providers for document chunks."""

import os
from abc import ABC, abstractmethod

from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential


class EmbeddingProvider(ABC):
    """Abstract base for embedding generation."""

    provider_name: str = ""
    model_name: str = ""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for a single text."""

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for multiple texts."""
        return [self.embed(text) for text in texts]

    def get_metadata(self) -> dict[str, str]:
        """Return metadata about the embedding model used."""
        return {"provider": self.provider_name, "model": self.model_name}


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using sentence-transformers.

    Defaults to a multilingual model suitable for Indic and European languages.
    This is the recommended default production embedding provider for the
    Knowledge Corpus, since it runs locally without per-call API cost and
    supports Sanskrit-transliteration and major Indic languages reasonably
    well via its multilingual training data.
    """

    provider_name = "sentence_transformers"

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((ImportError, ValueError)),
        reraise=True,
    )
    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((ImportError, ValueError)),
        reraise=True,
    )
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        return model.encode(texts).tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using OpenAI's embeddings API.

    Requires the ``openai`` package and ``OPENAI_API_KEY`` (or an explicit
    ``api_key``). Useful when a hosted, high-quality embedding model is
    preferred over a local sentence-transformers model.
    """

    provider_name = "openai"

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((ImportError, ValueError)),
        reraise=True,
    )
    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((ImportError, ValueError)),
        reraise=True,
    )
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        client = self._load_client()
        response = client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]


def get_embedding_provider(name: str | None = None, **kwargs: object) -> EmbeddingProvider:
    """Factory for embedding providers used by the Knowledge Corpus pipeline.

    If ``name`` is not provided, the provider is read from the
    ``EMBEDDING_PROVIDER`` environment variable (default: ``sentence_transformers``).
    If ``model_name`` is not provided, ``EMBEDDING_MODEL`` is used when set.
    """
    from divyadrishti.config import get_settings

    settings = get_settings()
    if name is None:
        name = settings.embedding_provider
    if "model_name" not in kwargs and settings.embedding_model:
        kwargs["model_name"] = settings.embedding_model

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


def get_default_embedding_provider() -> EmbeddingProvider:
    """Return an embedding provider configured from environment settings."""
    from divyadrishti.config import get_settings

    settings = get_settings()
    kwargs: dict[str, object] = {}
    if settings.embedding_model:
        kwargs["model_name"] = settings.embedding_model
    return get_embedding_provider(settings.embedding_provider, **kwargs)
