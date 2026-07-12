"""Public API for the Evidence and Rule Evaluation Engine."""

from divyadrishti.knowledge.models import Rule
from divyadrishti.reasoning.aggregator import EvidenceAggregator
from divyadrishti.reasoning.evaluator import RuleEvaluator
from divyadrishti.reasoning.models import ChartData, ReasoningTrace


class EvidenceEngine:
    """Evaluate retrieved rules against a chart and produce a ReasoningTrace."""

    def __init__(
        self,
        evaluator: RuleEvaluator | None = None,
        aggregator: EvidenceAggregator | None = None,
    ) -> None:
        self.evaluator = evaluator or RuleEvaluator()
        self.aggregator = aggregator or EvidenceAggregator()

    def evaluate(
        self,
        chart: dict | ChartData,
        question: str,
        rules: list[Rule],
    ) -> ReasoningTrace:
        """Run the full evidence pipeline.

        Steps:
          1. Parse the chart data.
          2. Evaluate each rule against the chart.
          3. Aggregate evidence, detect conflicts, and produce a trace.
        """
        if isinstance(chart, dict):
            chart_data = ChartData.model_validate(chart)
        else:
            chart_data = chart

        evidence = self.evaluator.evaluate_many(rules, chart_data, question)
        return self.aggregator.aggregate(question, chart_data, evidence)
