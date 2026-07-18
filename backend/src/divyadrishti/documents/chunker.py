"""Semantic chunking for document text."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from divyadrishti.documents.models import ChunkMetadata, Document, DocumentChunk

# Chapter markers across supported languages/transliterations: chapter,
# adhyaya (Sanskrit/Hindi), and generic numbered headings.
_CHAPTER_PATTERN = re.compile(r"(?i)\b(?:chapter|adhyaya)\s+([0-9]+|[ivxlcdm]+|\w+)\b")

# Section markers.
_SECTION_PATTERN = re.compile(r"(?i)\b(?:section)\s+([0-9]+|[ivxlcdm]+|\w+)\b")

# Verse markers: verse, shloka, sutra, or a standalone "N.M" style locant
# commonly used for chapter.verse numbering in classical texts.
_VERSE_PATTERN = re.compile(r"(?i)\b(?:verse|shloka|sloka|sutra)\s*[:\-]?\s*([0-9]+)\b")
_VERSE_LOCANT_PATTERN = re.compile(r"\b(\d{1,3})\.(\d{1,3})\b")


@dataclass
class _Unit:
    """A single semantic unit produced by the splitter."""

    text: str
    chapter: str = ""
    section: str = ""
    verse: str = ""
    is_heading: bool = False
    page_number: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class SemanticChunker:
    """Split document text into semantic chunks preserving headings and context."""

    def __init__(
        self, max_chunk_size: int = 800, overlap: int | None = None, overlap_percent: float = 0.15
    ) -> None:
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap if overlap is not None else int(max_chunk_size * overlap_percent)

    def chunk(
        self,
        document: Document,
        book_id: str = "",
        book_title: str = "",
        author: str = "",
        source_file: str = "",
    ) -> list[DocumentChunk]:
        """Split a document into semantic chunks."""
        units = self._split_into_units(document.raw_text)
        return self._build_chunks(
            units,
            book_id=book_id or document.metadata.get("book_id", ""),
            book_title=book_title or document.title or "",
            author=author or document.author or "",
            language=document.language,
            source_file=source_file or document.source_path,
        )

    def chunk_pages(
        self,
        pages: list[tuple[int, str]],
        document: Document,
        book_id: str = "",
        book_title: str = "",
        author: str = "",
        source_file: str = "",
    ) -> list[DocumentChunk]:
        """Split page-tagged text into chunks that preserve chapter, section, verse, and page."""
        all_units: list[_Unit] = []
        for page_number, page_text in pages:
            if not page_text or not page_text.strip():
                continue
            units = self._split_into_units(page_text)
            for unit in units:
                unit.page_number = page_number
            all_units.extend(units)

        return self._build_chunks(
            all_units,
            book_id=book_id or document.metadata.get("book_id", ""),
            book_title=book_title or document.title or "",
            author=author or document.author or "",
            language=document.language,
            source_file=source_file or document.source_path,
        )

    def _split_into_units(self, text: str) -> list[_Unit]:
        """Break text into semantic units (headings, verses, paragraphs)."""
        units: list[_Unit] = []
        for paragraph in [p.strip() for p in text.split("\n\n") if p.strip()]:
            heading = self._parse_heading(paragraph)
            if heading:
                units.append(heading)
                continue

            verse_units = self._parse_verse_units(paragraph)
            if verse_units:
                units.extend(verse_units)
                continue

            units.append(_Unit(text=paragraph))
        return units

    def _parse_heading(self, paragraph: str) -> _Unit | None:
        """Return a heading unit if the paragraph is a structural heading."""
        markdown = re.match(r"^(#{1,4})\s+(.+)$", paragraph)
        if markdown:
            heading_text = markdown.group(2).strip()
            chapter = self._infer_chapter_from_text(heading_text)
            return _Unit(
                text=paragraph,
                chapter=chapter,
                section=heading_text,
                is_heading=True,
            )

        chapter_match = re.match(
            r"(?i)^(?:chapter|adhyaya)\s+([0-9]+|[ivxlcdm]+|\w+)$", paragraph
        )
        if chapter_match:
            return _Unit(
                text=paragraph,
                chapter=chapter_match.group(1),
                section=paragraph,
                is_heading=True,
            )

        section_match = re.match(
            r"(?i)^(?:section)\s+([0-9]+|[ivxlcdm]+|\w+)$", paragraph
        )
        if section_match:
            return _Unit(
                text=paragraph,
                section=section_match.group(1),
                is_heading=True,
            )

        return None

    def _parse_verse_units(self, paragraph: str) -> list[_Unit] | None:
        """Split a paragraph into verse units when verse markers are present."""
        matches = list(_VERSE_PATTERN.finditer(paragraph))
        if not matches:
            matches = list(_VERSE_LOCANT_PATTERN.finditer(paragraph))
        if not matches:
            return None

        if len(matches) == 1:
            verse = matches[0].group(1)
            return [_Unit(text=paragraph, verse=verse)]

        segments: list[str] = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(paragraph)
            segment = paragraph[start:end].strip()
            if segment:
                segments.append(segment)

        return [_Unit(text=seg, verse=self._infer_verse(seg)) for seg in segments if seg]

    def _infer_chapter_from_text(self, text: str) -> str:
        """Infer chapter number from a heading or line of text."""
        match = _CHAPTER_PATTERN.search(text)
        if match:
            return match.group(1)
        return ""

    def _infer_verse(self, text: str) -> str:
        """Infer a verse number from an explicit marker or a chapter.verse locant."""
        match = _VERSE_PATTERN.search(text)
        if match:
            return match.group(1)
        locant_match = _VERSE_LOCANT_PATTERN.search(text)
        if locant_match:
            return locant_match.group(2)
        return ""

    def _build_chunks(
        self,
        units: list[_Unit],
        book_id: str,
        book_title: str,
        author: str,
        language: str,
        source_file: str,
    ) -> list[DocumentChunk]:
        """Assemble semantic units into chunks with ~15% overlap.

        Headings always start a fresh chunk so chapter/section boundaries are
        never crossed. Overlap is only applied between non-heading units.
        """
        chunks: list[DocumentChunk] = []
        current_units: list[_Unit] = []
        current_size = 0
        active_chapter = ""
        active_section = ""
        chunk_index = 0

        def _make_chunk(units_for_chunk: list[_Unit]) -> None:
            nonlocal chunk_index
            if not units_for_chunk:
                return
            chunk_text = "\n\n".join(u.text for u in units_for_chunk)
            page_number = next(
                (u.page_number for u in units_for_chunk if u.page_number is not None), None
            )
            chapter = next((u.chapter for u in units_for_chunk if u.chapter), active_chapter)
            section = next((u.section for u in units_for_chunk if u.section), active_section)
            verse = next((u.verse for u in units_for_chunk if u.verse), "")
            metadata = ChunkMetadata(
                book_id=book_id,
                book_title=book_title,
                author=author,
                language=language,
                chapter=chapter,
                section=section,
                verse=verse,
                page_number=page_number,
                source_file=source_file,
                chunk_index=chunk_index,
                original_text=chunk_text,
            )
            chunk = DocumentChunk(
                text=chunk_text, metadata=metadata, citation=metadata.build_citation()
            )
            chunks.append(chunk)
            chunk_index += 1

        for unit in units:
            unit_size = len(unit.text)

            if unit.is_heading:
                # Headings are structural boundaries: finalize current chunk
                # and start a new one. No overlap across a heading boundary.
                if current_units:
                    _make_chunk(current_units)
                    current_units = []
                    current_size = 0
                if unit.chapter:
                    active_chapter = unit.chapter
                if unit.section:
                    active_section = unit.section
                current_units.append(unit)
                current_size = unit_size
                continue

            # Inherit chapter/section context for non-heading units when not set.
            if not unit.chapter:
                unit.chapter = active_chapter
            if not unit.section:
                unit.section = active_section

            separator = 2 if current_units else 0
            if current_units and current_size + unit_size + separator > self.max_chunk_size:
                _make_chunk(current_units)
                overlap_units = self._select_overlap_units(current_units)
                current_units = overlap_units
                current_size = sum(len(u.text) for u in overlap_units) + max(
                    0, len(overlap_units) - 1
                ) * 2

            current_units.append(unit)
            current_size += unit_size + separator

        if current_units:
            _make_chunk(current_units)

        return chunks

    def _select_overlap_units(self, units: list[_Unit]) -> list[_Unit]:
        """Pick trailing units to prepend to the next chunk, preserving boundaries."""
        budget = min(self.overlap, sum(len(u.text) for u in units) // 2)
        selected: list[_Unit] = []
        size = 0
        for unit in reversed(units):
            add = len(unit.text) + (2 if selected else 0)
            if size + add <= budget:
                selected.insert(0, unit)
                size += add
            else:
                break
        return selected
