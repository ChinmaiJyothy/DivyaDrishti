"""Confidence Calculator for the Astrological Reasoning Engine."""

from divyadrishti.reasoning.models import Evidence


class ConfidenceCalculator:
    """Compute overall confidence from supporting and conflicting evidence."""

    def calculate(
        self,
        supporting: list[Evidence],
        conflicting: list[Evidence],
    ) -> float:
        """Return a confidence score between 0 and 100."""
        if not supporting:
            return 0.0

        total_weight = sum(ev.weight for ev in supporting)
        weighted_confidence = sum(ev.confidence * ev.weight for ev in supporting)

        if total_weight == 0:
            return 0.0

        base = weighted_confidence / total_weight

        conflict_penalty = sum(ev.weight for ev in conflicting)
        penalty = min(base, base * (conflict_penalty / max(total_weight, 1)))

        return round(max(0.0, min(100.0, base - penalty)), 2)

    def rule_confidence(self, evidence: list[Evidence]) -> float:
        """Compute average confidence from a list of evidence."""
        if not evidence:
            return 0.0
        return round(sum(ev.confidence for ev in evidence) / len(evidence), 2)
