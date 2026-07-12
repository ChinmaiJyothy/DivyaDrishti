"""Pydantic models for the Document Knowledge Processing Pipeline."""

import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata for a document chunk."""

    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    book_id: str
    book_title: str = ""
    author: str = ""
    language: str = ""
    chapter: str = ""
    section: str = ""
    verse: str = ""
    page_number: int | None = None
    topics: list[str] = Field(default_factory=list)
    subtopics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    original_text: str = ""
    translated_text: str | None = None
    source_file: str = ""
    chunk_index: int = 0

    def build_citation(self) -> str:
        """Generate a human-readable citation for this chunk."""
        parts = [
            self.book_title or self.book_id,
            f"Chapter {self.chapter}" if self.chapter else "",
            f"Verse {self.verse}" if self.verse else "",
            f"Page {self.page_number}" if self.page_number is not None else "",
            f"Chunk {self.chunk_index}",
        ]
        return ", ".join(p for p in parts if p)


class DocumentChunk(BaseModel):
    """A semantic chunk of a document."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    metadata: ChunkMetadata
    embedding: list[float] | None = None
    citation: str = ""

    def build_citation(self) -> str:
        """Generate a human-readable citation for this chunk."""
        return self.metadata.build_citation()


class Document(BaseModel):
    """A processed document."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_path: str
    file_type: str
    language: str = ""
    title: str = ""
    author: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_text: str = ""
    chunks: list[DocumentChunk] = Field(default_factory=list)

    def total_chunks(self) -> int:
        return len(self.chunks)


class DocumentProcessingResult(BaseModel):
    """Result of processing a document through the pipeline."""

    document: Document
    chunk_count: int
    language: str
    stored: bool
    errors: list[str] = Field(default_factory=list)


class DocumentSearchResult(BaseModel):
    """Result of a document retrieval query."""

    chunk: DocumentChunk
    score: float
    distance: float | None = None
