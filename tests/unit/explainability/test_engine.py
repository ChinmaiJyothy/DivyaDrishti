import pytest

from divyadrishti.explainability import ExplainabilityEngine
from divyadrishti.reasoning.astrological.models import AstrologicalChart, AstrologicalEntity, ReasoningResult
from divyadrishti.reasoning.models import Evidence


def sample_reasoning_result() -> ReasoningResult:
    return ReasoningResult(
        question="Will I have a happy marriage?",
        domain="marriage",
        relevant_factors=AstrologicalEntity(houses=[7], planets=["Jupiter"], topics=["marriage"]),
        matched_rules=[
            Evidence(
                rule_id="BPHS_7TH_001",
                source="BPHS",
                conditions=["Jupiter in 7th"],
                matched_conditions=["Jupiter in 7th"],
                confidence=85.0,
                weight=1.0,
                match_status="matched",
                explanation="Jupiter in 7th supports marriage.",
            )
        ],
        unmatched_rules=[
            Evidence(
                rule_id="BPHS_7TH_002",
                source="BPHS",
                conditions=["Saturn in 7th"],
                confidence=0.0,
                weight=1.0,
                match_status="not_matched",
            )
        ],
        supporting_evidence=[
            Evidence(
                rule_id="BPHS_7TH_001",
                source="BPHS",
                conditions=["Jupiter in 7th"],
                matched_conditions=["Jupiter in 7th"],
                confidence=85.0,
                weight=1.0,
                match_status="matched",
            )
        ],
        conflicting_evidence=[
            Evidence(
                rule_id="BPHS_7TH_003",
                source="BPHS",
                conditions=["Saturn aspect 7th"],
                confidence=20.0,
                weight=0.5,
                match_status="matched",
            )
        ],
        overall_confidence=82.0,
    )


def sample_chart() -> AstrologicalChart:
    return AstrologicalChart(
        lagna="Libra",
        moon_sign="Cancer",
        sun_sign="Leo",
        maha_dasha="Jupiter",
        antar_dasha="Saturn",
        planets={
            "Jupiter": {"house": 7, "sign": "Aries"},
            "Saturn": {"house": 10, "sign": "Capricorn"},
        },
    )


def test_explainability_report_generation():
    engine = ExplainabilityEngine()
    result = sample_reasoning_result()
    chart = sample_chart()

    report = engine.explain("Will I have a happy marriage?", chart, result)

    assert report.question == "Will I have a happy marriage?"
    assert report.detected_domain == "marriage"
    assert report.matched_rules
    assert report.ignored_rules
    assert report.supporting_evidence
    assert report.conflicting_evidence
    assert report.reasoning_path is not None
    assert report.confidence_score is not None
    assert report.classical_references is not None
    assert report.visualizations is not None
    assert report.limitations


def test_confidence_breakdown():
    engine = ExplainabilityEngine()
    report = engine.explain("?", sample_chart(), sample_reasoning_result())
    assert report.confidence_score.overall_confidence == 82.0
    assert any(c.type == "support" for c in report.confidence_score.contributors)
    assert any(c.type == "conflict" for c in report.confidence_score.contributors)


def test_reasoning_graph():
    from divyadrishti.explainability import ReasoningGraphBuilder

    builder = ReasoningGraphBuilder()
    graph = builder.build(sample_reasoning_result())
    assert graph.root.id == "question"
    assert any(child.id == "domain" for child in graph.root.children)


def test_rule_tracer():
    from divyadrishti.explainability import RuleTracer

    tracer = RuleTracer()
    trace = tracer.trace(sample_reasoning_result().matched_rules[0])
    assert trace.rule_id == "BPHS_7TH_001"
    assert trace.reason_included
    assert trace.match_status == "matched"


def test_visualization_data():
    from divyadrishti.explainability import ReasoningGraphBuilder, VisualizationBuilder

    result = sample_reasoning_result()
    graph = ReasoningGraphBuilder().build(result)
    vis = VisualizationBuilder().build(sample_chart(), result, graph)

    assert vis.decision_tree
    assert vis.reasoning_timeline
    assert vis.evidence_tree
    assert vis.planet_influence_graph
    assert vis.house_influence_graph
    assert vis.knowledge_source_graph


def test_explainability_includes_corpus_reference_fields():
    engine = ExplainabilityEngine()
    result = sample_reasoning_result()
    result.corpus_references = [
        {
            "corpus_id": 1,
            "corpus_name": "Test Corpus",
            "book": "BPHS",
            "chapter": "7",
            "verse": "5",
            "page": 12,
            "original_language": "sa",
            "original_text": "सप्तमे गुरौ सुखं दाम्पत्यम्।",
            "translated_text": "Jupiter in the 7th house gives marital happiness.",
            "score": 0.91,
        }
    ]
    report = engine.explain("Will I have a happy marriage?", sample_chart(), result)

    assert len(report.classical_references) == 1
    ref = report.classical_references[0]
    assert ref.book == "BPHS"
    assert ref.chapter == "7"
    assert ref.verse == "5"
    assert ref.page == "12"
    assert ref.original_language == "sa"
    assert ref.original_text
    assert ref.translated_text
    assert ref.retrieval_score == 0.91


def test_explainability_does_not_fabricate_references():
    engine = ExplainabilityEngine()
    result = sample_reasoning_result()
    result.corpus_references = []
    report = engine.explain("Will I have a happy marriage?", sample_chart(), result)

    assert report.classical_references == []
    assert any("never fabricated" in note.lower() for note in report.important_notes)
