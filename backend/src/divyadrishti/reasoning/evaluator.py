"""RuleEvaluator evaluates individual rules against a birth chart."""

from divyadrishti.knowledge.models import Rule
from divyadrishti.reasoning.models import ChartData, Evidence
from divyadrishti.reasoning.scoring import build_evidence, match_factors


class RuleEvaluator:
    """Evaluate a single Vedic astrology rule against a chart."""

    def evaluate(self, rule: Rule, chart: ChartData, question: str = "") -> Evidence:
        """Return an Evidence object for the rule and chart."""
        matched = match_factors(rule.astrological_factors, chart)
        if not matched or not any(matched.values()):
            return Evidence(
                rule_id=rule.rule_id,
                source=rule.source_book,
                conditions=rule.conditions,
                matched_conditions=[],
                confidence=0.0,
                weight=0.0,
                match_status="not_matched",
                explanation=rule.interpretation,
                notes="No matching astrological factors in the chart.",
            )

        return build_evidence(rule, chart, matched)

    def evaluate_many(self, rules: list[Rule], chart: ChartData, question: str = "") -> list[Evidence]:
        """Evaluate a list of rules and return only matched evidence."""
        evidence = [self.evaluate(rule, chart, question) for rule in rules]
        return [ev for ev in evidence if ev.confidence > 0]
