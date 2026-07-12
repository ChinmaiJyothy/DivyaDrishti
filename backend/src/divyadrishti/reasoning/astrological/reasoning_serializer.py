"""Reasoning Serializer for the Astrological Reasoning Engine."""

from divyadrishti.reasoning.astrological.models import ReasoningResult
from divyadrishti.reasoning.models import ReasoningTrace


class ReasoningSerializer:
    """Serialize the final reasoning result into a ReasoningTrace."""

    def serialize(self, result: ReasoningResult) -> ReasoningTrace:
        """Convert the reasoning result to a ReasoningTrace."""
        return ReasoningTrace(
            question=result.question,
            domain=result.domain,
            chart_data=result.relevant_factors.model_dump(),
            relevant_factors=result.relevant_factors.model_dump(),
            matched_rules=result.matched_rules,
            supporting_evidence=result.supporting_evidence,
            conflicting_evidence=result.conflicting_evidence,
            overall_confidence=result.overall_confidence,
            reasoning_summary=result.reasoning_summary,
            reasoning_steps=[step.model_dump() for step in result.reasoning_steps],
            suggested_follow_up_topics=result.suggested_follow_up_topics,
        )
