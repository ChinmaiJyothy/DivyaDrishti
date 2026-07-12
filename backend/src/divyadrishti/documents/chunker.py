"""Semantic chunking for document text."""

import re
from pathlib import Path

from divyadrishti.documents.models import ChunkMetadata, Document, DocumentChunk


class SemanticChunker:
    """Split document text into semantic chunks preserving headings and context."""

    def __init__(self, max_chunk_size: int = 800, overlap: int = 100) -> None:
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document: Document,
        book_id: str = "",
        book_title: str = "",
        author: str = "",
        source_file: str = "",
    ) -> list[DocumentChunk]:
        """Split a document into semantic chunks."""
        sections = self._split_by_headings(document.raw_text)
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for section in sections:
            heading, body = section
            topic = heading.strip("#\n ").strip()
            pieces = self._split_into_pieces(body)

            for piece in pieces:
                metadata = ChunkMetadata(
                    book_id=book_id or document.metadata.get("book_id", ""),
                    book_title=book_title or document.title or "",
                    author=author or document.author or "",
                    language=document.language,
                    chapter=self._infer_chapter(heading),
                    section=topic,
                    source_file=source_file or document.source_path,
                    chunk_index=chunk_index,
                    original_text=piece,
                )
                chunk = DocumentChunk(
                    text=piece,
                    metadata=metadata,
                    citation=metadata.build_citation(),
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _split_by_headings(self, text: str) -> list[tuple[str, str]]:
        """Split text by Markdown-style headings."""
        pattern = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)
        parts = pattern.split(text)
        sections = []

        if len(parts) == 1:
            return [("", text)]

        if not parts[0].strip().startswith("#"):
            sections.append(("", parts[0]))
            parts = parts[1:]

        for i in range(0, len(parts) - 1, 2):
            heading = parts[i]
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((heading, body))

        return sections

    def _split_into_pieces(self, text: str) -> list[str]:
        """Split a section into chunks of roughly max_chunk_size with overlap."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        pieces: list[str] = []
        current = ""

        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 2 > self.max_chunk_size and current:
                pieces.append(current.strip())
                current = current[-self.overlap:] if self.overlap else ""
            current += ("\n\n" if current else "") + paragraph

        if current:
            pieces.append(current.strip())

        return pieces

    def _infer_chapter(self, heading: str) -> str:
        """Infer chapter number from a heading."""
        match = re.search(r"(?i)chapter\s+(\d+|\w+)", heading)
        if match:
            return match.group(1)
        return ""
