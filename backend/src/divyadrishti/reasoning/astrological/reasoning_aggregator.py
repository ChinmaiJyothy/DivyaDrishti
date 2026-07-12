"""Reasoning Aggregator for the Astrological Reasoning Engine."""

from divyadrishti.reasoning.astrological.models import (
    AstrologicalEntity,
    ReasoningResult,
    ReasoningStep,
)
from divyadrishti.reasoning.models import Evidence


class ReasoningAggregator:
    """Aggregate evidence, conflicts, and confidence into structured reasoning."""

    def aggregate(
        self,
        question: str,
        domain: str,
        relevant_factors: AstrologicalEntity,
        evidence: list[Evidence],
        supporting: list[Evidence],
        conflicting: list[Evidence],
        overall_confidence: float,
        follow_up_topics: list[str],
    ) -> ReasoningResult:
        """Build the final reasoning result."""
        matched = [ev for ev in evidence if ev.match_status == "matched"]
        partial = [ev for ev in evidence if ev.match_status == "partially_matched"]
        unmatched = [ev for ev in evidence if ev.match_status == "not_matched"]

        steps = self._build_steps(question, domain, relevant_factors, evidence)

        return ReasoningResult(
            question=question,
            domain=domain,
            relevant_factors=relevant_factors,
            matched_rules=matched,
            partially_matched_rules=partial,
            unmatched_rules=unmatched,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            overall_confidence=overall_confidence,
            reasoning_summary=self._build_summary(question, domain, matched, conflicting),
            reasoning_steps=steps,
            suggested_follow_up_topics=follow_up_topics,
        )

    def _build_steps(
        self,
        question: str,
        domain: str,
        relevant_factors: AstrologicalEntity,
        evidence: list[Evidence],
    ) -> list[ReasoningStep]:
        """Create a trace of reasoning steps."""
        steps = [
            ReasoningStep(
                step="Question Analysis",
                details=f"Domain: {domain}. Relevant factors: {relevant_factors.model_dump()}",
            ),
            ReasoningStep(
                step="Rule Retrieval",
                details=f"Retrieved {len(evidence)} rules for evaluation.",
            ),
            ReasoningStep(
                step="Evidence Evaluation",
                details=f"Matched {sum(1 for ev in evidence if ev.match_status == 'matched')} rules fully.",
                evidence=[ev.rule_id for ev in evidence if ev.match_status == "matched"],
            ),
            ReasoningStep(
                step="Conflict Resolution",
                details=f"Conflicting evidence: {sum(1 for ev in evidence if ev.conflicting)}.",
                evidence=[ev.rule_id for ev in evidence if ev.conflicting],
            ),
        ]
        return steps

    def _build_summary(
        self,
        question: str,
        domain: str,
        matched: list[Evidence],
        conflicting: list[Evidence],
    ) -> str:
        """Build a structured, non-natural-language summary."""
        summary = f"Domain={domain}. Matched={len(matched)}. Conflicting={len(conflicting)}."
        if matched:
            summary += " Primary: " + ", ".join(m.rule_id for m in matched[:3])
        return summary
