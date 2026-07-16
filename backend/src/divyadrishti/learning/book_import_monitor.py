"""Book Import Monitor for analyzing new astrology books."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.documents import DocumentProcessingPipeline
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.constants import register_book_source
from divyadrishti.knowledge.models import Book, Rule
from divyadrishti.learning.conflict_analyzer import ConflictAnalyzer


class IngestionFinding(BaseModel):
    """A single finding from a book ingestion."""

    type: str
    message: str
    chunk_id: str | None = None
    rule_id: str | None = None


class IngestionReport(BaseModel):
    """Report produced after importing a new book."""

    book_id: str
    book_title: str
    chunk_count: int
    candidate_rules: list[Rule] = Field(default_factory=list)
    findings: list[IngestionFinding] = Field(default_factory=list)
    new_topics: list[str] = Field(default_factory=list)


class BookImportMonitor:
    """Process new books and generate an ingestion report without activating rules."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        pipeline: DocumentProcessingPipeline,
    ) -> None:
        self.repository = repository
        self.pipeline = pipeline
        self.conflict_analyzer = ConflictAnalyzer(repository)

    def process(
        self,
        file_path: Path | str,
        book_id: str,
        book_title: str,
        metadata: dict[str, Any] | None = None,
    ) -> IngestionReport:
        """Process a new book and return an ingestion report."""
        register_book_source(book_id, book_title)
        self.repository.add_book(
            Book(book_id=book_id, title=book_title, **(metadata or {}))
        )

        result = self.pipeline.process(
            file_path,
            book_id=book_id,
            book_title=book_title,
            metadata=metadata,
        )

        findings: list[IngestionFinding] = []
        candidates: list[Rule] = []
        new_topics: set[str] = set()

        existing_topics = {rule.topic for rule in self.repository.list_rules(enabled_only=False)}

        for i, chunk in enumerate(result.document.chunks):
            candidate = self._create_candidate(chunk, book_id, book_title, i)
            candidates.append(candidate)

            findings.extend(self._check_metadata(chunk, i))
            findings.extend(self._check_reference(chunk, i))

            chunk_topics = set(chunk.metadata.topics or [])
            new_topics.update(chunk_topics - existing_topics)

            for rule in self.repository.list_rules(enabled_only=False):
                if self._is_duplicate(candidate, rule):
                    findings.append(
                        IngestionFinding(
                            type="duplicate",
                            message=f"Chunk {i} similar to existing rule {rule.rule_id}",
                            chunk_id=chunk.id,
                            rule_id=rule.rule_id,
                        )
                    )
                if self._is_conflict(candidate, rule):
                    findings.append(
                        IngestionFinding(
                            type="conflict",
                            message=f"Chunk {i} conflicts with rule {rule.rule_id}",
                            chunk_id=chunk.id,
                            rule_id=rule.rule_id,
                        )
                    )

        return IngestionReport(
            book_id=book_id,
            book_title=book_title,
            chunk_count=result.chunk_count,
            candidate_rules=candidates,
            findings=findings,
            new_topics=sorted(new_topics),
        )

    def _create_candidate(self, chunk, book_id: str, book_title: str, index: int) -> Rule:
        from datetime import datetime, timezone

        return Rule(
            rule_id=f"{book_id.upper()}_CANDIDATE_{index:04d}",
            source_book=book_id,
            topic=chunk.metadata.topics[0] if chunk.metadata.topics else book_title,
            category="general",
            conditions=[chunk.text[:200]],
            interpretation=chunk.text,
            confidence=0.5,
            approval_status="pending",
            enabled=False,
            created_at=datetime.now(timezone.utc).isoformat(),
            modified_at=datetime.now(timezone.utc).isoformat(),
        )

    def _check_metadata(self, chunk, index: int) -> list[IngestionFinding]:
        findings = []
        if not chunk.metadata.topics:
            findings.append(
                IngestionFinding(type="missing_metadata", message=f"Chunk {index} has no topics", chunk_id=chunk.id)
            )
        if not chunk.metadata.keywords:
            findings.append(
                IngestionFinding(type="missing_metadata", message=f"Chunk {index} has no keywords", chunk_id=chunk.id)
            )
        return findings

    def _check_reference(self, chunk, index: int) -> list[IngestionFinding]:
        findings = []
        meta = chunk.metadata
        has_detail = meta.chapter or meta.verse or meta.page_number is not None
        if not has_detail:
            findings.append(
                IngestionFinding(type="incomplete_reference", message=f"Chunk {index} citation incomplete", chunk_id=chunk.id)
            )
        return findings

    def _is_duplicate(self, candidate: Rule, rule: Rule) -> bool:
        cand_text = candidate.interpretation.lower()
        rule_text = rule.interpretation.lower()
        return cand_text in rule_text or rule_text in cand_text or cand_text == rule_text

    def _is_conflict(self, candidate: Rule, rule: Rule) -> bool:
        if candidate.topic != rule.topic:
            return False
        from divyadrishti.reasoning.sentiment import sentiments_match

        return not sentiments_match(candidate.interpretation, rule.interpretation)
