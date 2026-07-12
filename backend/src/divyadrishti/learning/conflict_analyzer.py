"""Conflict Analyzer for detecting duplicate and contradictory rules."""

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.models import Rule
from divyadrishti.reasoning.sentiment import classify_sentiment, sentiments_match


class ConflictAnalyzer:
    """Detect duplicate and conflicting rules."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def find_duplicates(self) -> list[tuple[str, str, str]]:
        """Return pairs of similar rule IDs and reasons."""
        duplicates = []
        rules = self.repository.list_rules(enabled_only=False)
        for i, a in enumerate(rules):
            for b in rules[i + 1 :]:
                if self._similar(a, b):
                    duplicates.append((a.rule_id, b.rule_id, "similar factors"))
        return duplicates

    def find_conflicts(self) -> list[tuple[str, str, str]]:
        """Return pairs of conflicting rule IDs and reasons."""
        conflicts = []
        rules = self.repository.list_rules(enabled_only=False)
        for i, a in enumerate(rules):
            for b in rules[i + 1 :]:
                if self._same_scope(a, b) and not sentiments_match(a.interpretation, b.interpretation):
                    conflicts.append((a.rule_id, b.rule_id, "opposite interpretation"))
        return conflicts

    def _similar(self, a: Rule, b: Rule) -> bool:
        """Heuristic: rules share the same factors and similar interpretation."""
        if a.astrological_factors != b.astrological_factors:
            return False
        return sentiments_match(a.interpretation, b.interpretation)

    def _same_scope(self, a: Rule, b: Rule) -> bool:
        """Heuristic: rules target the same topic and factors."""
        if a.topic != b.topic:
            return False
        return a.astrological_factors == b.astrological_factors
