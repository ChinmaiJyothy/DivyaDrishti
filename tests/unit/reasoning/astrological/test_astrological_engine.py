import pytest

from divyadrishti.knowledge import Rule
from divyadrishti.knowledge.models import AstrologicalFactors
from divyadrishti.knowledge.repository import KnowledgeRepository
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.reasoning.astrological import (
    AstrologicalChart,
    AstrologicalReasoningEngine,
    QuestionAnalyzer,
    ReasoningRequest,
)


@pytest.fixture
def knowledge_engine(tmp_path):
    repo = KnowledgeRepository(tmp_path)
    return KnowledgeRetrievalEngine(repo)


def make_chart():
    return AstrologicalChart(
        maha_dasha="Jupiter",
        antar_dasha="Saturn",
        planets={
            "Jupiter": {"house": 7, "sign": "Libra", "nakshatra": "Swati"},
            "Saturn": {"house": 7, "sign": "Libra", "nakshatra": "Swati"},
            "Venus": {"house": 1, "sign": "Aries"},
        },
        yogas=["Gaja Kesari"],
        doshas=["Manglik"],
    )


def test_question_analyzer_detects_domain():
    analyzer = QuestionAnalyzer()
    chart = make_chart()
    domain, factors, follow_up = analyzer.analyze("When will I get married?", chart)
    assert domain == "marriage"
    assert 7 in factors.houses
    assert "Venus" in factors.planets
    assert "Jupiter" in factors.dashas


def test_question_analyzer_detects_career():
    analyzer = QuestionAnalyzer()
    chart = make_chart()
    domain, factors, _ = analyzer.analyze("Will I get a promotion?", chart)
    assert domain == "career"
    assert 10 in factors.houses


def test_astrological_engine_marriage_reasoning(knowledge_engine):
    repo = knowledge_engine.repository
    repo.add_rule(
        Rule(
            rule_id="BPHS_7TH_001",
            source_book="BPHS",
            topic="Marriage",
            category="marriage",
            conditions=["Jupiter in 7th"],
            astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
            interpretation="Happy marriage.",
            confidence=0.8,
        ),
        save=False,
    )
    repo.add_rule(
        Rule(
            rule_id="BPHS_7TH_002",
            source_book="BPHS",
            topic="Marriage",
            category="marriage",
            conditions=["Saturn in 7th"],
            astrological_factors=AstrologicalFactors(houses=[7], planets=["Saturn"]),
            interpretation="Delayed marriage.",
            confidence=0.7,
        ),
        save=False,
    )

    engine = AstrologicalReasoningEngine(knowledge_engine)
    request = ReasoningRequest(
        question="Will I have a happy marriage?",
        chart=make_chart(),
    )
    result = engine.reason(request)

    assert result.domain == "marriage"
    assert len(result.matched_rules) == 2
    assert len(result.conflicting_evidence) == 1
    assert result.overall_confidence > 0


def test_astrological_engine_trace(knowledge_engine):
    repo = knowledge_engine.repository
    repo.add_rule(
        Rule(
            rule_id="BPHS_7TH_001",
            source_book="BPHS",
            topic="Marriage",
            category="marriage",
            conditions=["Jupiter in 7th"],
            astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
            interpretation="Happy marriage.",
            confidence=0.8,
        ),
        save=False,
    )

    engine = AstrologicalReasoningEngine(knowledge_engine)
    request = ReasoningRequest(
        question="Will I have a happy marriage?",
        chart=make_chart(),
    )
    trace = engine.reason_trace(request)

    assert trace.domain == "marriage"
    assert trace.matched_rules
    assert trace.relevant_factors
    assert trace.suggested_follow_up_topics
