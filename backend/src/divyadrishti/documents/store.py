"""Vector stores for document chunks."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from divyadrishti.documents.models import DocumentChunk, DocumentSearchResult


class VectorStore(ABC):
    """Abstract base for a vector store of document chunks."""

    @abstractmethod
    def add(self, chunks: list[DocumentChunk]) -> None:
        """Add chunks to the store."""

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Search for similar chunks by embedding."""


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store for tests."""

    def __init__(self) -> None:
        self.chunks: list[DocumentChunk] = []

    def add(self, chunks: list[DocumentChunk]) -> None:
        self.chunks.extend(chunks)

    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        import numpy as np

        def cosine(a: list[float], b: list[float]) -> float:
            a_arr = np.array(a)
            b_arr = np.array(b)
            return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

        results = []
        for chunk in self.chunks:
            if not chunk.embedding:
                continue
            if filters and not self._matches_filters(chunk, filters):
                continue
            score = cosine(embedding, chunk.embedding)
            results.append(DocumentSearchResult(chunk=chunk, score=score, distance=1 - score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:n_results]

    def _matches_filters(self, chunk: DocumentChunk, filters: dict[str, Any]) -> bool:
        for key, value in filters.items():
            attr = getattr(chunk.metadata, key, None)
            if isinstance(value, list):
                if attr not in value:
                    return False
            elif attr != value:
                return False
        return True


class ChromaVectorStore(VectorStore):
    """Persistent vector store backed by ChromaDB."""

    def __init__(self, collection_name: str = "documents", persist_dir: Path | str = ".chroma"):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        ids = [chunk.id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks if chunk.embedding]
        metadatas = [self._clean_metadata(chunk.metadata.model_dump()) for chunk in chunks]
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    @staticmethod
    def _clean_metadata(metadata: dict) -> dict:
        """Remove empty lists and None values to satisfy ChromaDB constraints."""
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                continue
            if value == [] or value == {}:
                continue
            if value == "" and key not in {"title", "book_title", "author", "source_file"}:
                continue
            cleaned[key] = value
        return cleaned

    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        query_kwargs: dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if filters:
            query_kwargs["where"] = filters

        results = self.collection.query(**query_kwargs)

        search_results: list[DocumentSearchResult] = []
        if not results["ids"]:
            return search_results

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for idx, doc_id in enumerate(ids):
            metadata = metadatas[idx] if metadatas else {}
            from divyadrishti.documents.models import ChunkMetadata

            chunk = DocumentChunk(
                id=doc_id,
                text=documents[idx] if documents else "",
                metadata=ChunkMetadata.model_validate(metadata),
                embedding=list(embedding),
            )
            chunk.citation = chunk.build_citation()
            score = 1 - distances[idx] if distances else 0.0
            search_results.append(DocumentSearchResult(chunk=chunk, score=score, distance=distances[idx]))

        return search_results
