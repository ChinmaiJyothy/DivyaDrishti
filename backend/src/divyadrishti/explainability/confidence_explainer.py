"""Confidence Explainer for the Explainability Engine."""

from divyadrishti.explainability.models import ConfidenceBreakdown, ConfidenceContribution
from divyadrishti.reasoning.astrological.models import ReasoningResult


class ConfidenceExplainer:
    """Break down overall confidence into individual contributions."""

    def explain(self, result: ReasoningResult) -> ConfidenceBreakdown:
        """Return a confidence breakdown with supporting and conflicting contributors."""
        contributors: list[ConfidenceContribution] = []

        for ev in result.supporting_evidence:
            name = ev.rule_id or ev.explanation or "Supporting evidence"
            contributors.append(
                ConfidenceContribution(
                    name=name,
                    contribution=round(ev.confidence * ev.weight, 2),
                    type="support",
                )
            )

        for ev in result.conflicting_evidence:
            name = ev.rule_id or ev.explanation or "Conflicting evidence"
            contributors.append(
                ConfidenceContribution(
                    name=name,
                    contribution=-round(ev.confidence * ev.weight, 2),
                    type="conflict",
                )
            )

        return ConfidenceBreakdown(
            overall_confidence=result.overall_confidence,
            contributors=contributors,
        )
