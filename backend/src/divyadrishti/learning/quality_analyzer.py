"""Rule Quality Analyzer for scoring rule quality."""

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning.feedback_manager import FeedbackManager
from divyadrishti.learning.models import QualityMetrics


class QualityAnalyzer:
    """Analyze rule quality from usage, feedback, and conflict data."""

    def __init__(self, repository: KnowledgeRepository, feedback: FeedbackManager) -> None:
        self.repository = repository
        self.feedback = feedback

    def analyze(self, rule_id: str) -> QualityMetrics:
        """Return quality metrics for a rule."""
        rule = self.repository.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        rule_feedback = self.feedback.for_rule(rule_id)
        positive = sum(1 for f in rule_feedback if f.rating in {"Very Helpful", "Helpful"})
        negative = sum(1 for f in rule_feedback if f.rating in {"Not Helpful", "Incorrect"})

        usage = rule.usage_count
        retrieval = rule.usage_count
        conflicts = len(rule.interpretation) % 5  # Placeholder heuristic

        score = self._compute_score(
            usage,
            positive,
            negative,
            conflicts,
            rule.confidence,
        )

        return QualityMetrics(
            rule_id=rule_id,
            usage_count=usage,
            positive_feedback=positive,
            negative_feedback=negative,
            conflict_frequency=conflicts,
            retrieval_frequency=retrieval,
            confidence_stability=rule.confidence,
            quality_score=score,
        )

    def analyze_all(self) -> list[QualityMetrics]:
        """Return quality metrics for all rules."""
        return [self.analyze(rule.rule_id) for rule in self.repository.list_rules(enabled_only=False)]

    def _compute_score(
        self,
        usage: int,
        positive: int,
        negative: int,
        conflicts: int,
        confidence: float,
    ) -> float:
        """Compute a quality score between 0 and 100."""
        if usage == 0:
            return round(confidence * 50, 2)

        feedback_score = (positive - negative * 2) / max(usage, 1)
        conflict_penalty = conflicts * 10
        base = (confidence * 100) + (feedback_score * 20)
        return round(max(0.0, min(100.0, base - conflict_penalty)), 2)
