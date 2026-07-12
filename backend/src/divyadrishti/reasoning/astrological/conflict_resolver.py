"""Conflict Resolver for the Astrological Reasoning Engine."""

from divyadrishti.reasoning.conflict import resolve_conflicts
from divyadrishti.reasoning.models import Evidence


class ConflictResolver:
    """Detect and resolve conflicts between evidence."""

    def resolve(
        self,
        evidence: list[Evidence],
        question: str = "",
    ) -> tuple[list[Evidence], list[Evidence]]:
        """Return supporting and conflicting evidence lists."""
        return resolve_conflicts(evidence, question)
