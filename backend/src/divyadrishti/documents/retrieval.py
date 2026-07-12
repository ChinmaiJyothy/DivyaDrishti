"""Document retrieval engine for semantic and hybrid search."""

from typing import Any

from divyadrishti.documents.embeddings import EmbeddingProvider
from divyadrishti.documents.models import DocumentSearchResult
from divyadrishti.documents.store import VectorStore


class DocumentRetrievalEngine:
    """Retrieve document chunks by topic, house, planet, yoga, dosha, citation, or semantic query."""

    def __init__(self, store: VectorStore, embedder: EmbeddingProvider) -> None:
        self.store = store
        self.embedder = embedder

    def semantic_search(self, query: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by natural language query."""
        embedding = self.embedder.embed(query)
        return self.store.query(embedding, n_results=n_results)

    def search_by_topic(self, topic: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by exact topic metadata."""
        embedding = self.embedder.embed(topic)
        return self.store.query(
            embedding,
            n_results=n_results,
            filters={"topics": topic},
        )

    def search_by_house(self, house: int | str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by house number."""
        query = f"house {house}"
        embedding = self.embedder.embed(query)
        return self.store.query(embedding, n_results=n_results)

    def search_by_planet(self, planet: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by planet name."""
        embedding = self.embedder.embed(planet)
        return self.store.query(embedding, n_results=n_results)

    def search_by_yoga(self, yoga: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by yoga name."""
        embedding = self.embedder.embed(yoga)
        return self.store.query(embedding, n_results=n_results)

    def search_by_dosha(self, dosha: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by dosha name."""
        embedding = self.embedder.embed(dosha)
        return self.store.query(embedding, n_results=n_results)

    def hybrid_search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        n_results: int = 5,
    ) -> list[DocumentSearchResult]:
        """Combine semantic and metadata filter search."""
        embedding = self.embedder.embed(query)
        return self.store.query(embedding, n_results=n_results, filters=filters)

    def search_by_citation(self, book_id: str, n_results: int = 5) -> list[DocumentSearchResult]:
        """Search by exact book ID."""
        embedding = self.embedder.embed(book_id)
        return self.store.query(
            embedding,
            n_results=n_results,
            filters={"book_id": book_id},
        )
