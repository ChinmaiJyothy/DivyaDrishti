"""Test-only fake embedding provider."""

import hashlib
import random

from divyadrishti.documents.embeddings import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic, dependency-free embedding provider for unit tests."""

    provider_name = "fake"
    model_name = "fake-v1"

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        return [round(rng.random(), 6) for _ in range(self.dimension)]
