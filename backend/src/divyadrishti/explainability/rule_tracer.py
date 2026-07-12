"""Rule Tracer for the Explainability Engine."""

from divyadrishti.explainability.models import RuleTrace
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.reasoning.models import Evidence


class RuleTracer:
    """Create traceable RuleTrace objects from Evidence and rules."""

    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self.repository = repository

    def trace(self, evidence: Evidence) -> RuleTrace:
        """Convert an Evidence object into a RuleTrace with reason included/excluded."""
        rule = None
        if self.repository:
            rule = self.repository.get_rule(evidence.rule_id)

        source_book = rule.source_book if rule else evidence.source
        chapter = rule.chapter if rule else None
        verse = rule.verse if rule else None

        if evidence.match_status in {"matched", "partially_matched"} and evidence.confidence > 0:
            reason_included = f"Matched conditions: {', '.join(evidence.matched_conditions or evidence.conditions)}"
            reason_excluded = ""
        else:
            reason_included = ""
            reason_excluded = f"Did not match conditions: {evidence.conditions}"

        return RuleTrace(
            rule_id=evidence.rule_id,
            source_book=source_book,
            chapter=chapter,
            verse=verse,
            conditions=evidence.conditions,
            matched_conditions=evidence.matched_conditions,
            weight=evidence.weight,
            confidence=evidence.confidence,
            match_status=evidence.match_status,
            reason_included=reason_included,
            reason_excluded=reason_excluded,
        )

    def trace_all(self, evidence_list: list[Evidence]) -> list[RuleTrace]:
        """Trace all evidence items."""
        return [self.trace(ev) for ev in evidence_list]
