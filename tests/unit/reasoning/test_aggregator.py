from divyadrishti.knowledge import Rule
from divyadrishti.knowledge.models import AstrologicalFactors
from divyadrishti.reasoning import ChartData, Evidence, EvidenceAggregator
from divyadrishti.reasoning.models import PlanetPosition


def make_evidence(rule_id, interpretation, confidence, weight, conditions=None):
    return Evidence(
        rule_id=rule_id,
        source="BPHS",
        conditions=conditions or ["Test"],
        matched_conditions=["Matched"],
        confidence=confidence,
        weight=weight,
        explanation=interpretation,
    )


def test_aggregator_deduplicates():
    ev = make_evidence("BPHS_7TH_001", "Happy marriage.", 80.0, 2.0)
    aggregator = EvidenceAggregator()
    trace = aggregator.aggregate("Will I marry?", ChartData(), [ev, ev])
    assert len(trace.matched_rules) == 1


def test_aggregator_supporting_conflicting():
    supporting = make_evidence("BPHS_7TH_001", "Happy marriage.", 85.0, 2.0)
    conflicting = make_evidence("BPHS_7TH_002", "Delayed marriage.", 70.0, 1.5)
    chart = ChartData()
    aggregator = EvidenceAggregator()
    trace = aggregator.aggregate("Will I have a happy marriage?", chart, [supporting, conflicting])

    assert len(trace.supporting_evidence) == 1
    assert len(trace.conflicting_evidence) == 1
    assert trace.supporting_evidence[0].rule_id == "BPHS_7TH_001"
    assert trace.conflicting_evidence[0].rule_id == "BPHS_7TH_002"
    assert 0 <= trace.overall_confidence <= 100


def test_aggregator_summary():
    ev = make_evidence("BPHS_7TH_001", "Happy marriage.", 85.0, 2.0)
    aggregator = EvidenceAggregator()
    trace = aggregator.aggregate("Will I have a happy marriage?", ChartData(), [ev])
    assert "Question: Will I have a happy marriage?" in trace.reasoning_summary
    assert "Supporting evidence" in trace.reasoning_summary
