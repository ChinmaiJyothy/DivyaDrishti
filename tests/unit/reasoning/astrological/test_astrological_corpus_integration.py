"""Tests for Knowledge Corpus integration into the Reasoning Engine."""

import pytest

from divyadrishti.documents import DocumentChunk, InMemoryVectorStore
from divyadrishti.documents.models import ChunkMetadata
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.hybrid_retrieval import CorpusRetrievalEngine
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.models import CandidateRule, CandidateRuleStatus
from divyadrishti.reasoning.astrological import (
    AstrologicalChart,
    AstrologicalReasoningEngine,
    ReasoningRequest,
)
from divyadrishti.reasoning.astrological.models import AstrologicalEntity
from tests.unit.documents.fake_provider import FakeEmbeddingProvider


def _make_corpus_candidate(chunk_id: str, text: str) -> CandidateRule:
    return CandidateRule(
        candidate_rule_id=f"CAND_{chunk_id}",
        corpus_id=1,
        book_id=1,
        source_book_title="Test Corpus Book",
        language="en",
        chapter="1",
        verse="5",
        original_text=text,
        translated_text=None,
        topic="marriage",
        subtopic=None,
        astrological_factors_json={
            "planets": ["Jupiter"],
            "houses": [7],
            "signs": [],
            "nakshatras": [],
            "yogas": [],
            "doshas": [],
            "dashas": [],
        },
        candidate_conditions_json=["Jupiter in house 7"],
        candidate_interpretation=text,
        confidence=0.85,
        status=CandidateRuleStatus.APPROVED.value,
        chunk_id=chunk_id,
    )


def _make_chart() -> AstrologicalChart:
    return AstrologicalChart(
        maha_dasha="Jupiter",
        planets={
            "Jupiter": {"house": 7, "sign": "Libra", "nakshatra": "Swati"},
        },
    )


def _build_corpus_engine(candidate: CandidateRule):
    embedder = FakeEmbeddingProvider()
    chunk = DocumentChunk(
        id=candidate.chunk_id,
        text=candidate.candidate_interpretation,
        metadata=ChunkMetadata(
            book_id=str(candidate.book_id),
            book_title=candidate.source_book_title,
            language="en",
            chapter=candidate.chapter,
            verse=candidate.verse,
        ),
        embedding=embedder.embed(candidate.candidate_interpretation),
    )
    store = InMemoryVectorStore()
    store.add([chunk])

    return CorpusRetrievalEngine(
        vector_store=store,
        embedder=embedder,
        approved_candidates=[candidate],
        corpus_authority={1: 1.0},
        corpus_names={1: "Test Corpus"},
    )


@pytest.fixture
def file_knowledge_engine(tmp_path):
    repository = KnowledgeRepository(tmp_path)
    return KnowledgeRetrievalEngine(repository)


def test_reasoning_uses_corpus_engine_and_injects_references(file_knowledge_engine):
    candidate = _make_corpus_candidate("chunk-corpus-1", "Jupiter in the 7th house brings a happy marriage.")
    corpus_engine = _build_corpus_engine(candidate)

    engine = AstrologicalReasoningEngine(
        file_knowledge_engine,
        corpus_engine=corpus_engine,
    )

    request = ReasoningRequest(
        question="Will I have a happy marriage?",
        chart=_make_chart(),
    )
    result = engine.reason(request)

    assert result.corpus_retrieval_method != "disabled"
    assert result.corpus_references
    assert any("Jupiter" in str(ref) for ref in result.corpus_references)
    assert result.matched_rules


def test_reasoning_trace_passes_corpus_fields(file_knowledge_engine):
    candidate = _make_corpus_candidate("chunk-corpus-2", "Jupiter in the 7th house indicates a pleasant married life.")
    corpus_engine = _build_corpus_engine(candidate)

    engine = AstrologicalReasoningEngine(
        file_knowledge_engine,
        corpus_engine=corpus_engine,
    )

    request = ReasoningRequest(
        question="Tell me about my marriage",
        chart=_make_chart(),
    )
    trace = engine.reason_trace(request)

    assert trace.corpus_retrieval_method != "disabled"
    assert trace.corpus_references
    assert isinstance(trace.corpus_related_chapters, list)


def test_reasoning_without_corpus_engine_is_backward_compatible(file_knowledge_engine):
    engine = AstrologicalReasoningEngine(file_knowledge_engine)

    request = ReasoningRequest(
        question="Will I have a happy marriage?",
        chart=_make_chart(),
    )
    result = engine.reason(request)

    assert result.corpus_retrieval_method == "disabled"
    assert result.corpus_references == []
    assert result.corpus_related_chapters == []
