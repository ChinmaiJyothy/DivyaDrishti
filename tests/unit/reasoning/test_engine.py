from divyadrishti.knowledge import Rule
from divyadrishti.knowledge.models import AstrologicalFactors
from divyadrishti.reasoning import ChartData, EvidenceEngine
from divyadrishti.reasoning.models import PlanetPosition


def test_engine_evaluate():
    rule = Rule(
        rule_id="BPHS_7TH_001",
        source_book="BPHS",
        topic="Marriage",
        category="marriage",
        conditions=["Jupiter in 7th"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
        interpretation="Happy marriage.",
        confidence=0.8,
    )

    chart = {
        "planets": {
            "Jupiter": {"house": 7, "sign": "Libra"},
        },
    }

    engine = EvidenceEngine()
    trace = engine.evaluate(chart, "Will I have a happy marriage?", [rule])

    assert trace.question == "Will I have a happy marriage?"
    assert len(trace.matched_rules) == 1
    assert trace.matched_rules[0].rule_id == "BPHS_7TH_001"
    assert trace.overall_confidence > 0


def test_engine_with_conflict():
    happy = Rule(
        rule_id="BPHS_7TH_001",
        source_book="BPHS",
        topic="Marriage",
        category="marriage",
        conditions=["Jupiter in 7th"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
        interpretation="Happy marriage.",
        confidence=0.8,
    )
    delay = Rule(
        rule_id="BPHS_7TH_002",
        source_book="BPHS",
        topic="Marriage",
        category="marriage",
        conditions=["Saturn in 7th"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Saturn"]),
        interpretation="Delayed marriage.",
        confidence=0.7,
    )

    chart = ChartData(
        planets={
            "Jupiter": PlanetPosition(house=7, sign="Libra"),
            "Saturn": PlanetPosition(house=7, sign="Libra"),
        }
    )

    engine = EvidenceEngine()
    trace = engine.evaluate(chart, "Will I have a happy marriage?", [happy, delay])

    assert len(trace.matched_rules) == 2
    assert len(trace.supporting_evidence) == 1
    assert len(trace.conflicting_evidence) == 1
