"""Explainable Astrology Engine (XAI) for DivyaDrishti."""

from divyadrishti.explainability.confidence_explainer import ConfidenceExplainer
from divyadrishti.explainability.evidence_explainer import EvidenceExplainer
from divyadrishti.explainability.models import ExplainabilityReport, Limitation
from divyadrishti.explainability.reasoning_graph_builder import ReasoningGraphBuilder
from divyadrishti.explainability.reference_collector import ReferenceCollector
from divyadrishti.explainability.rule_tracer import RuleTracer
from divyadrishti.explainability.visualization_builder import VisualizationBuilder
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.reasoning.astrological.models import AstrologicalChart, ReasoningResult


class ExplainabilityEngine:
    """Generate structured explainability reports from astrological reasoning."""

    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self.repository = repository
        self.graph_builder = ReasoningGraphBuilder()
        self.rule_tracer = RuleTracer(repository)
        self.evidence_explainer = EvidenceExplainer()
        self.confidence_explainer = ConfidenceExplainer()
        self.visualization_builder = VisualizationBuilder()
        self.reference_collector = ReferenceCollector(repository)

    def explain(
        self,
        question: str,
        chart: AstrologicalChart,
        result: ReasoningResult,
    ) -> ExplainabilityReport:
        """Build an ExplainabilityReport from a ReasoningResult."""
        graph = self.graph_builder.build(result)
        matched = self.rule_tracer.trace_all(result.matched_rules)
        partially_matched = self.rule_tracer.trace_all(result.partially_matched_rules)
        unmatched = self.rule_tracer.trace_all(result.unmatched_rules)
        ignored = partially_matched + unmatched
        supporting, conflicting = self.evidence_explainer.explain_all(
            result.supporting_evidence, result.conflicting_evidence
        )
        confidence = self.confidence_explainer.explain(result)
        references = self.reference_collector.collect(
            result.supporting_evidence + result.conflicting_evidence
        )
        suggested_reading = self.reference_collector.suggest_reading(result.domain, result.matched_rules)
        visualizations = self.visualization_builder.build(chart, result, graph)

        chart_factors = self._chart_factors(chart)

        return ExplainabilityReport(
            question=question,
            detected_domain=result.domain,
            chart_factors_used=chart_factors,
            rules_considered=[r.rule_id for r in result.matched_rules + result.partially_matched_rules + result.unmatched_rules],
            matched_rules=matched,
            ignored_rules=ignored,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            reasoning_path=graph,
            confidence_score=confidence,
            limitations=self._derive_limitations(result),
            classical_references=references,
            suggested_reading=suggested_reading,
            important_notes=[
                "This explanation is generated from the structured reasoning engine.",
                "Classical references are derived from the knowledge base and not fabricated.",
                "Confidence reflects rule quality and evidence agreement, not certainty.",
            ],
            visualizations=visualizations,
        )

    def _chart_factors(self, chart: AstrologicalChart) -> dict:
        return {
            "lagna": chart.lagna,
            "moon_sign": chart.moon_sign,
            "sun_sign": chart.sun_sign,
            "maha_dasha": chart.maha_dasha,
            "antar_dasha": chart.antar_dasha,
            "planets": chart.planets,
            "navamsa": chart.navamsa,
            "yogas": chart.yogas,
            "doshas": chart.doshas,
        }

    def _derive_limitations(self, result: ReasoningResult) -> list[Limitation]:
        limitations = []

        if result.overall_confidence < 50:
            limitations.append(
                Limitation(type="low_confidence", description="Overall confidence is below 50%.")
            )

        if result.conflicting_evidence:
            limitations.append(
                Limitation(
                    type="conflicting_rules",
                    description=f"{len(result.conflicting_evidence)} conflicting evidence items reduce certainty.",
                )
            )

        if not result.matched_rules:
            limitations.append(
                Limitation(type="insufficient_evidence", description="No rules fully matched the chart.")
            )

        if not result.relevant_factors.dashas:
            limitations.append(
                Limitation(type="missing_dasha", description="Dasha timing information not available.")
            )

        return limitations
