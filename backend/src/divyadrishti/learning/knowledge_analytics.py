"""Knowledge Analytics for usage, coverage, and trust metrics."""

from collections import Counter
from typing import Any

from divyadrishti.knowledge import KnowledgeRepository


class KnowledgeAnalytics:
    """Generate analytics over the knowledge base and feedback."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def most_used_books(self, n: int = 5) -> list[tuple[str, int]]:
        """Return the most referenced source books."""
        counts = Counter(rule.source_book for rule in self.repository.list_rules(enabled_only=False))
        return counts.most_common(n)

    def most_referenced_chapters(self, n: int = 5) -> list[tuple[str, int]]:
        """Return the most referenced chapters."""
        counts = Counter(
            rule.chapter for rule in self.repository.list_rules(enabled_only=False) if rule.chapter
        )
        return counts.most_common(n)

    def most_common_topics(self, n: int = 5) -> list[tuple[str, int]]:
        """Return the most common rule topics."""
        counts = Counter(rule.topic for rule in self.repository.list_rules(enabled_only=False))
        return counts.most_common(n)

    def knowledge_coverage(self) -> dict[str, Any]:
        """Return a summary of knowledge coverage."""
        rules = self.repository.list_rules(enabled_only=False)
        topics = {rule.topic for rule in rules}
        books = {rule.source_book for rule in rules}
        return {
            "total_rules": len(rules),
            "enabled_rules": len(self.repository.list_rules(enabled_only=True)),
            "pending_rules": len([r for r in rules if r.approval_status == "pending"]),
            "deprecated_rules": len([r for r in rules if r.deprecated]),
            "unique_topics": len(topics),
            "unique_books": len(books),
        }

    def unused_rules(self, min_usage: int = 0) -> list[str]:
        """Return rule IDs with usage below the threshold."""
        return [
            rule.rule_id
            for rule in self.repository.list_rules(enabled_only=False)
            if rule.usage_count <= min_usage
        ]

    def frequently_conflicting_rules(self, conflict_pairs: list[tuple[str, str, str]]) -> list[tuple[str, int]]:
        """Return rule IDs that appear frequently in conflict pairs."""
        counts = Counter()
        for a, b, _ in conflict_pairs:
            counts[a] += 1
            counts[b] += 1
        return counts.most_common()

    def most_trusted_rules(self, n: int = 5) -> list[tuple[str, int]]:
        """Return rules with the highest positive feedback."""
        rules = sorted(
            self.repository.list_rules(enabled_only=False),
            key=lambda r: r.positive_feedback,
            reverse=True,
        )
        return [(r.rule_id, r.positive_feedback) for r in rules[:n]]
