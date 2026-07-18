"""Hybrid semantic + keyword retrieval for the Knowledge Corpus.

Combines:
    - Semantic similarity (cosine distance over corpus embeddings)
    - Rule confidence (from administrator-reviewed candidate rules)
    - Classical authority (per-corpus authority weight)
    - Topic relevance (question <-> rule topic overlap)
    - User question relevance (keyword overlap)
    - Recent administrator approval (recency boost)

Falls back to the existing keyword-based ``KnowledgeRetrievalEngine``
when the vector store is empty, unavailable, or raises an error, so the
Reasoning Engine never fails outright due to a semantic search issue.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from divyadrishti.documents.embeddings import EmbeddingProvider
from divyadrishti.documents.store import VectorStore
from divyadrishti.knowledge.constants import register_book_source
from divyadrishti.knowledge.models import AstrologicalFactors, Rule
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.models import CandidateRule
from divyadrishti.reasoning.astrological.models import AstrologicalEntity

logger = logging.getLogger(__name__)

# Ranking weights. Documented in docs/SEMANTIC_RETRIEVAL.md.
WEIGHT_SEMANTIC_SIMILARITY = 0.35
WEIGHT_RULE_CONFIDENCE = 0.20
WEIGHT_CLASSICAL_AUTHORITY = 0.15
WEIGHT_TOPIC_RELEVANCE = 0.10
WEIGHT_METADATA_RELEVANCE = 0.10
WEIGHT_RECENCY = 0.10

RECENCY_WINDOW_DAYS = 90


def _normalize_rule_id(rule_id: str) -> str:
    """Return a rule id that satisfies the strict ``^[A-Z][A-Z0-9_]*$`` pattern."""
    normalized = "".join(c if c.isalnum() else "_" for c in rule_id).upper()
    # Collapse repeated underscores and strip trailing underscores.
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.rstrip("_")


class CorpusReference(BaseModel):
    """A retrieved classical reference, suitable for the Explainability Engine."""

    corpus_id: int
    corpus_name: str
    book: str
    chapter: str | None = None
    verse: str | None = None
    page: int | None = None
    original_language: str | None = None
    original_text: str = ""
    translated_text: str | None = None
    score: float = 0.0


class CorpusRetrievalResult(BaseModel):
    """Result of a hybrid corpus retrieval query."""

    rules: list[Rule] = Field(default_factory=list)
    supporting_verses: list[CorpusReference] = Field(default_factory=list)
    related_chapters: list[str] = Field(default_factory=list)
    retrieval_method: str = "hybrid"  # hybrid | keyword_fallback | empty


@dataclass
class _ScoredCandidate:
    candidate: CandidateRule
    corpus_name: str
    semantic_score: float
    original_text: str
    language: str | None
    score: float = 0.0
    matched_conditions: list[str] = field(default_factory=list)


def candidate_rule_to_domain_rule(candidate: CandidateRule) -> Rule:
    """Convert an approved ``CandidateRule`` DB row into a knowledge ``Rule``.

    Registers the source book title so the strict ``Rule`` validator
    (which requires known book identifiers) accepts corpus-sourced books
    without manual registration.
    """
    book_id = f"CORPUS_{candidate.book_id}"
    register_book_source(book_id, candidate.source_book_title)

    factors = candidate.astrological_factors_json or {}
    rule_id = _normalize_rule_id(
        candidate.approved_rule_id or f"CORPUS_{candidate.candidate_rule_id}"
    )
    return Rule(
        rule_id=rule_id,
        source_book=book_id,
        chapter=candidate.chapter,
        verse=candidate.verse,
        topic=candidate.topic,
        subtopic=candidate.subtopic,
        category=candidate.topic or "classical-texts",
        conditions=candidate.candidate_conditions_json or [],
        astrological_factors=AstrologicalFactors(
            houses=factors.get("houses", []),
            planets=factors.get("planets", []),
            signs=factors.get("signs", []),
            nakshatras=factors.get("nakshatras", []),
            yogas=factors.get("yogas", []),
            doshas=factors.get("doshas", []),
            dashas=factors.get("dashas", []),
            topics=factors.get("topics", []),
        ),
        interpretation=candidate.candidate_interpretation,
        confidence=candidate.confidence,
        references=[candidate.source_book_title],
        approval_status="approved",
    )


class CorpusRetrievalEngine:
    """Hybrid retrieval engine scoped to one or more Knowledge Corpora."""

    def __init__(
        self,
        vector_store: VectorStore | None,
        embedder: EmbeddingProvider | None,
        approved_candidates: list[CandidateRule],
        corpus_authority: dict[int, float] | None = None,
        corpus_names: dict[int, str] | None = None,
        keyword_engine: KnowledgeRetrievalEngine | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder
        self.approved_candidates = approved_candidates
        self.corpus_authority = corpus_authority or {}
        self.corpus_names = corpus_names or {}
        self.keyword_engine = keyword_engine
        self._by_chunk_id = {c.chunk_id: c for c in approved_candidates if c.chunk_id}

    def retrieve(
        self,
        question: str,
        entities: AstrologicalEntity,
        corpus_ids: list[int] | None = None,
        n_results: int = 8,
    ) -> CorpusRetrievalResult:
        """Retrieve structured rules, supporting verses, and chapters for a question."""
        candidates = self.approved_candidates
        if corpus_ids is not None:
            candidates = [c for c in candidates if c.corpus_id in corpus_ids]

        if not candidates:
            return CorpusRetrievalResult(retrieval_method="empty")

        if self.vector_store is None or self.embedder is None:
            return self._keyword_fallback(entities, candidates)

        try:
            scored = self._semantic_rank(question, entities, candidates, n_results, corpus_ids)
        except Exception as exc:
            logger.warning("Semantic corpus retrieval failed, falling back to keyword search: %s", exc)
            return self._keyword_fallback(entities, candidates)

        if not scored:
            return self._keyword_fallback(entities, candidates)

        rules = [candidate_rule_to_domain_rule(item.candidate) for item in scored]
        supporting_verses = [
            CorpusReference(
                corpus_id=item.candidate.corpus_id,
                corpus_name=self.corpus_names.get(item.candidate.corpus_id, "Unknown Corpus"),
                book=item.candidate.source_book_title,
                chapter=item.candidate.chapter,
                verse=item.candidate.verse,
                page=item.candidate.page,
                original_language=item.language,
                original_text=item.original_text,
                translated_text=item.candidate.translated_text,
                score=round(item.score, 4),
            )
            for item in scored
        ]
        related_chapters = list(
            dict.fromkeys(
                f"{item.candidate.source_book_title} - Chapter {item.candidate.chapter}"
                for item in scored
                if item.candidate.chapter
            )
        )

        return CorpusRetrievalResult(
            rules=rules,
            supporting_verses=supporting_verses,
            related_chapters=related_chapters,
            retrieval_method="hybrid",
        )

    def _semantic_rank(
        self,
        question: str,
        entities: AstrologicalEntity,
        candidates: list[CandidateRule],
        n_results: int,
        corpus_ids: list[int] | None,
    ) -> list[_ScoredCandidate]:
        embedding = self.embedder.embed(question)
        filters: dict = {}
        if corpus_ids is not None:
            filters["corpus_id"] = corpus_ids
        search_results = self.vector_store.query(embedding, n_results=max(n_results * 3, 10), filters=filters or None)

        scored: list[_ScoredCandidate] = []
        for result in search_results:
            chunk_id = result.chunk.id
            candidate = self._by_chunk_id.get(chunk_id)
            if candidate is None:
                continue

            semantic_score = max(0.0, min(1.0, result.score))
            authority = self.corpus_authority.get(candidate.corpus_id, 1.0)
            topic_relevance = self._topic_relevance(entities, candidate)
            metadata_relevance = self._metadata_relevance(question, candidate)
            recency = self._recency_boost(candidate)

            composite = (
                WEIGHT_SEMANTIC_SIMILARITY * semantic_score
                + WEIGHT_RULE_CONFIDENCE * candidate.confidence
                + WEIGHT_CLASSICAL_AUTHORITY * min(authority, 1.0)
                + WEIGHT_TOPIC_RELEVANCE * topic_relevance
                + WEIGHT_METADATA_RELEVANCE * metadata_relevance
                + WEIGHT_RECENCY * recency
            )

            scored.append(
                _ScoredCandidate(
                    candidate=candidate,
                    corpus_name=self.corpus_names.get(candidate.corpus_id, "Unknown Corpus"),
                    semantic_score=semantic_score,
                    original_text=result.chunk.metadata.original_text or result.chunk.text,
                    language=result.chunk.metadata.language,
                    score=composite,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:n_results]

    def _topic_relevance(self, entities: AstrologicalEntity, candidate: CandidateRule) -> float:
        if not entities.topics:
            return 0.0
        return 1.0 if candidate.topic in entities.topics else 0.0

    def _metadata_relevance(self, question: str, candidate: CandidateRule) -> float:
        """Score how well question terms match candidate metadata."""
        question_words = {w.lower() for w in question.split() if len(w) > 3}
        if not question_words:
            return 0.0

        factors = candidate.astrological_factors_json or {}
        metadata_texts = [
            candidate.topic,
            candidate.subtopic,
            candidate.source_book_title,
            candidate.chapter,
            candidate.verse,
            " ".join(str(v) for v in factors.get("planets", [])),
            " ".join(str(v) for v in factors.get("houses", [])),
            " ".join(str(v) for v in factors.get("signs", [])),
            " ".join(str(v) for v in factors.get("yogas", [])),
            " ".join(str(v) for v in factors.get("doshas", [])),
            " ".join(str(v) for v in factors.get("dashas", [])),
        ]
        metadata_words = set()
        for text in metadata_texts:
            if text:
                metadata_words.update(str(text).lower().split())
        metadata_words = {w for w in metadata_words if len(w) > 3}

        overlap = question_words & metadata_words
        return min(1.0, len(overlap) / max(len(question_words), 1))

    def _recency_boost(self, candidate: CandidateRule) -> float:
        if not candidate.reviewed_at:
            return 0.0
        reviewed_at = candidate.reviewed_at
        if reviewed_at.tzinfo is None:
            reviewed_at = reviewed_at.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - reviewed_at).days
        if age_days < 0:
            return 1.0
        return max(0.0, 1.0 - (age_days / RECENCY_WINDOW_DAYS))

    def _keyword_fallback(
        self, entities: AstrologicalEntity, candidates: list[CandidateRule]
    ) -> CorpusRetrievalResult:
        """Fall back to structured-factor overlap when semantic search is unavailable."""
        matched: list[CandidateRule] = []
        for candidate in candidates:
            factors = candidate.astrological_factors_json or {}
            if (
                set(factors.get("planets", [])) & set(entities.planets)
                or set(factors.get("houses", [])) & set(entities.houses)
                or set(factors.get("yogas", [])) & set(entities.yogas)
                or set(factors.get("doshas", [])) & set(entities.doshas)
                or set(factors.get("dashas", [])) & set(entities.dashas)
                or candidate.topic in entities.topics
            ):
                matched.append(candidate)

        if not matched:
            return CorpusRetrievalResult(retrieval_method="keyword_fallback")

        rules = [candidate_rule_to_domain_rule(c) for c in matched]
        supporting_verses = [
            CorpusReference(
                corpus_id=c.corpus_id,
                corpus_name=self.corpus_names.get(c.corpus_id, "Unknown Corpus"),
                book=c.source_book_title,
                chapter=c.chapter,
                verse=c.verse,
                page=c.page,
                original_language=c.language,
                original_text=c.original_text,
                translated_text=c.translated_text,
                score=c.confidence,
            )
            for c in matched
        ]
        return CorpusRetrievalResult(
            rules=rules,
            supporting_verses=supporting_verses,
            related_chapters=list(
                dict.fromkeys(f"{c.source_book_title} - Chapter {c.chapter}" for c in matched if c.chapter)
            ),
            retrieval_method="keyword_fallback",
        )
