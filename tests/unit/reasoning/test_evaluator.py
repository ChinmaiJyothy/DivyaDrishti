from divyadrishti.knowledge import Rule
from divyadrishti.knowledge.models import AstrologicalFactors
from divyadrishti.reasoning import ChartData, RuleEvaluator
from divyadrishti.reasoning.models import PlanetPosition


def test_evaluator_matches_rule():
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
    chart = ChartData(planets={"Jupiter": PlanetPosition(house=7, sign="Libra")})
    evaluator = RuleEvaluator()
    ev = evaluator.evaluate(rule, chart)
    assert ev.rule_id == "BPHS_7TH_001"
    assert ev.confidence > 0
    assert "Matched Jupiter in house 7" in ev.matched_conditions


def test_evaluator_no_match():
    rule = Rule(
        rule_id="BPHS_7TH_002",
        source_book="BPHS",
        topic="Marriage",
        category="marriage",
        conditions=["Saturn in 7th"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Saturn"]),
        interpretation="Delayed marriage.",
        confidence=0.7,
    )
    chart = ChartData(planets={"Jupiter": PlanetPosition(house=7, sign="Libra")})
    evaluator = RuleEvaluator()
    ev = evaluator.evaluate(rule, chart)
    assert ev.confidence == 0.0


def test_evaluator_many():
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
    chart = ChartData(planets={"Jupiter": PlanetPosition(house=7, sign="Libra")})
    evaluator = RuleEvaluator()
    evidence = evaluator.evaluate_many([rule], chart)
    assert len(evidence) == 1
