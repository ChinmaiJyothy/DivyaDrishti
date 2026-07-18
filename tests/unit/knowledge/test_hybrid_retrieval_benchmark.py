"""Benchmarks and correctness tests for hybrid corpus retrieval."""

import time

from divyadrishti.documents import DocumentChunk, InMemoryVectorStore
from divyadrishti.documents.models import ChunkMetadata
from divyadrishti.knowledge.hybrid_retrieval import CorpusRetrievalEngine
from divyadrishti.models import CandidateRule, CandidateRuleStatus
from divyadrishti.reasoning.astrological.models import AstrologicalEntity
from tests.unit.documents.fake_provider import FakeEmbeddingProvider


def _make_candidate(
    chunk_id: str,
    corpus_id: int,
    source_book_title: str,
    topic: str,
    interpretation: str,
    confidence: float,
    planets: list[str] | None = None,
    houses: list[int] | None = None,
    reviewed_at=None,
):
    return CandidateRule(
        candidate_rule_id=f"CAND_{chunk_id}",
        corpus_id=corpus_id,
        book_id=1,
        source_book_title=source_book_title,
        language="en",
        chapter="1",
        verse="1",
        original_text=interpretation,
        translated_text=None,
        topic=topic,
        subtopic=None,
        astrological_factors_json={
            "planets": planets or [],
            "houses": houses or [],
            "signs": [],
            "nakshatras": [],
            "yogas": [],
            "doshas": [],
            "dashas": [],
        },
        candidate_conditions_json=["condition"],
        candidate_interpretation=interpretation,
        confidence=confidence,
        status=CandidateRuleStatus.APPROVED.value,
        chunk_id=chunk_id,
        reviewed_at=reviewed_at,
    )


def _store_chunks(store, embedder, chunks_data):
    for chunk_id, text, corpus_id in chunks_data:
        chunk = DocumentChunk(
            id=chunk_id,
            text=text,
            metadata=ChunkMetadata(
                book_id="1",
                book_title="Test Book",
                language="en",
            ),
            embedding=embedder.embed(text),
        )
        store.add([chunk])


def test_hybrid_ranking_prefers_higher_confidence():
    store = InMemoryVectorStore()
    embedder = FakeEmbeddingProvider()

    chunks = [
        ("chunk-1", "Jupiter in the 7th house brings a happy marriage.", 1),
        ("chunk-2", "Saturn in the 7th house delays marriage.", 1),
    ]
    _store_chunks(store, embedder, chunks)

    candidates = [
        _make_candidate(
            "chunk-1", 1, "Test Book", "marriage", "Jupiter in the 7th house brings a happy marriage.", 0.95, planets=["Jupiter"], houses=[7]
        ),
        _make_candidate(
            "chunk-2", 1, "Test Book", "marriage", "Saturn in the 7th house delays marriage.", 0.40, planets=["Saturn"], houses=[7]
        ),
    ]

    engine = CorpusRetrievalEngine(
        vector_store=store,
        embedder=embedder,
        approved_candidates=candidates,
        corpus_authority={1: 1.0},
        corpus_names={1: "Test Corpus"},
    )

    entities = AstrologicalEntity(houses=[7], planets=["Jupiter"], topics=["marriage"])
    result = engine.retrieve("What does Jupiter in the 7th house mean for marriage?", entities, n_results=2)

    assert result.retrieval_method == "hybrid"
    assert len(result.rules) == 2
    assert result.rules[0].rule_id == "CORPUS_CAND_CHUNK_1"
    assert result.supporting_verses[0].score >= result.supporting_verses[1].score


def test_keyword_fallback_when_vector_store_unavailable():
    candidates = [
        _make_candidate(
            "chunk-3", 1, "Test Book", "career", "Sun in the 10th house gives leadership.", 0.80, planets=["Sun"], houses=[10]
        ),
    ]

    engine = CorpusRetrievalEngine(
        vector_store=None,
        embedder=None,
        approved_candidates=candidates,
        corpus_authority={1: 1.0},
        corpus_names={1: "Test Corpus"},
    )

    entities = AstrologicalEntity(planets=["Sun"], houses=[10])
    result = engine.retrieve("Tell me about Sun in 10th house", entities)

    assert result.retrieval_method == "keyword_fallback"
    assert len(result.rules) == 1
    assert result.rules[0].rule_id == "CORPUS_CAND_CHUNK_3"


def test_metadata_relevance_boosts_matching_topic():
    store = InMemoryVectorStore()
    embedder = FakeEmbeddingProvider()

    text = "Venus in the 7th house indicates a pleasant marriage."
    chunk_id = "chunk-4"
    chunk = DocumentChunk(
        id=chunk_id,
        text=text,
        metadata=ChunkMetadata(book_id="1", book_title="Test Book", language="en"),
        embedding=embedder.embed(text),
    )
    store.add([chunk])

    candidate = _make_candidate(
        chunk_id, 1, "Test Book", "marriage", text, 0.70, planets=["Venus"], houses=[7]
    )

    engine = CorpusRetrievalEngine(
        vector_store=store,
        embedder=embedder,
        approved_candidates=[candidate],
        corpus_authority={1: 1.0},
        corpus_names={1: "Test Corpus"},
    )

    entities = AstrologicalEntity(planets=["Venus"], houses=[7])
    result = engine.retrieve("marriage and Venus influence", entities)

    assert result.retrieval_method == "hybrid"
    assert len(result.rules) == 1
    assert result.supporting_verses[0].corpus_name == "Test Corpus"


def test_retrieval_latency_under_threshold():
    store = InMemoryVectorStore()
    embedder = FakeEmbeddingProvider()

    candidates = []
    chunks = []
    for i in range(50):
        chunk_id = f"chunk-{i}"
        text = f"Rule {i}: Jupiter in the {i % 12 + 1}th house gives result {i}."
        chunks.append((chunk_id, text, 1))
        candidates.append(
            _make_candidate(
                chunk_id,
                1,
                "Test Book",
                "general",
                text,
                0.5 + (i % 50) / 100,
                planets=["Jupiter"],
                houses=[i % 12 + 1],
            )
        )
    _store_chunks(store, embedder, chunks)

    engine = CorpusRetrievalEngine(
        vector_store=store,
        embedder=embedder,
        approved_candidates=candidates,
        corpus_authority={1: 1.0},
        corpus_names={1: "Test Corpus"},
    )

    entities = AstrologicalEntity(planets=["Jupiter"])
    start = time.perf_counter()
    result = engine.retrieve("Jupiter influence", entities, n_results=8)
    elapsed = time.perf_counter() - start

    assert result.retrieval_method == "hybrid"
    assert len(result.rules) == 8
    assert elapsed < 1.0
