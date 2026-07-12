"""Evidence Explainer for the Explainability Engine."""

from divyadrishti.explainability.models import EvidenceExplanation
from divyadrishti.reasoning.models import Evidence


class EvidenceExplainer:
    """Explain why supporting and conflicting evidence matters."""

    def explain_supporting(self, evidence: Evidence) -> EvidenceExplanation:
        """Explain a supporting evidence factor."""
        why = evidence.explanation or f"Rule {evidence.rule_id} conditions were met in the chart."
        return EvidenceExplanation(
            factor=evidence.rule_id,
            why_it_matters=why,
            rule_id=evidence.rule_id,
            source=evidence.source,
            confidence_impact=evidence.confidence * evidence.weight,
        )

    def explain_conflicting(self, evidence: Evidence) -> EvidenceExplanation:
        """Explain a conflicting evidence factor."""
        why = evidence.explanation or f"Rule {evidence.rule_id} conflicts with other evidence."
        return EvidenceExplanation(
            factor=evidence.rule_id,
            why_it_matters=why,
            rule_id=evidence.rule_id,
            source=evidence.source,
            confidence_impact=-evidence.confidence * evidence.weight,
        )

    def explain_all(
        self, supporting: list[Evidence], conflicting: list[Evidence]
    ) -> tuple[list[EvidenceExplanation], list[EvidenceExplanation]]:
        """Explain all supporting and conflicting evidence."""
        return (
            [self.explain_supporting(ev) for ev in supporting],
            [self.explain_conflicting(ev) for ev in conflicting],
        )
