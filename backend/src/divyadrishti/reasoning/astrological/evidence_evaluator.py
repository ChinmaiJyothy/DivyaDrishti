"""Evidence Evaluator for the Astrological Reasoning Engine."""

from divyadrishti.knowledge.models import Rule
from divyadrishti.reasoning.astrological.models import AstrologicalChart
from divyadrishti.reasoning.evaluator import RuleEvaluator
from divyadrishti.reasoning.models import Evidence


class EvidenceEvaluator:
    """Evaluate retrieved rules against the birth chart."""

    def __init__(self, evaluator: RuleEvaluator | None = None) -> None:
        self.evaluator = evaluator or RuleEvaluator()

    def evaluate(
        self,
        rules: list[Rule],
        chart: AstrologicalChart,
        question: str = "",
    ) -> list[Evidence]:
        """Evaluate every rule and return structured evidence."""
        chart_data = chart.to_chart_data()
        return [self.evaluator.evaluate(rule, chart_data, question) for rule in rules]
