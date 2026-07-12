"""EvidenceAggregator combines, ranks, and summarizes evidence."""

from divyadrishti.reasoning.conflict import detect_conflicts, resolve_conflicts
from divyadrishti.reasoning.models import ChartData, Evidence, ReasoningTrace
from divyadrishti.reasoning.sentiment import classify_sentiment


class EvidenceAggregator:
    """Aggregate evidence from many rules into a structured reasoning trace."""

    def aggregate(
        self,
        question: str,
        chart: ChartData,
        evidence: list[Evidence],
    ) -> ReasoningTrace:
        """Combine evidence, resolve conflicts, and produce a ReasoningTrace."""
        evidence = self._deduplicate(evidence)
        evidence = self._rank(evidence)
        evidence = self._annotate_relationships(evidence)

        supporting, conflicting = resolve_conflicts(evidence, question)
        overall = self._overall_confidence(supporting, conflicting)
        summary = self._summary(question, supporting, conflicting)

        return ReasoningTrace(
            question=question,
            chart_data=chart.model_dump(),
            matched_rules=evidence,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            overall_confidence=overall,
            reasoning_summary=summary,
        )

    def _deduplicate(self, evidence: list[Evidence]) -> list[Evidence]:
        seen: set[str] = set()
        unique: list[Evidence] = []
        for ev in evidence:
            if ev.rule_id not in seen:
                seen.add(ev.rule_id)
                unique.append(ev)
        return unique

    def _rank(self, evidence: list[Evidence]) -> list[Evidence]:
        return sorted(evidence, key=lambda ev: (ev.weight, ev.confidence), reverse=True)

    def _annotate_relationships(self, evidence: list[Evidence]) -> list[Evidence]:
        conflicts = detect_conflicts(evidence)
        conflict_map: dict[str, set[str]] = {ev.rule_id: set() for ev in evidence}
        for a, b in conflicts:
            conflict_map[a].add(b)
            conflict_map[b].add(a)

        updated: list[Evidence] = []
        for ev in evidence:
            ev_sentiment = classify_sentiment(ev.explanation)
            supporting_ids: list[str] = []
            conflicting_ids: list[str] = []

            for other in evidence:
                if other.rule_id == ev.rule_id:
                    continue
                if other.rule_id in conflict_map[ev.rule_id]:
                    conflicting_ids.append(other.rule_id)
                else:
                    supporting_ids.append(other.rule_id)

            updated.append(ev.model_copy(update={
                "supporting": supporting_ids,
                "conflicting": conflicting_ids,
            }))
        return updated

    def _overall_confidence(
        self,
        supporting: list[Evidence],
        conflicting: list[Evidence],
    ) -> float:
        if not supporting and not conflicting:
            return 0.0

        support_score = sum(ev.confidence * ev.weight for ev in supporting)
        conflict_score = sum(ev.confidence * ev.weight for ev in conflicting)
        total_weight = sum(ev.weight for ev in supporting + conflicting)

        if total_weight == 0:
            return 0.0

        net = (support_score - conflict_score) / total_weight
        return round(max(0.0, min(100.0, net)), 2)

    def _summary(
        self,
        question: str,
        supporting: list[Evidence],
        conflicting: list[Evidence],
    ) -> str:
        lines: list[str] = []
        lines.append(f"Question: {question}")

        if supporting:
            lines.append("Supporting evidence:")
            for ev in supporting[:3]:
                lines.append(f"  - {ev.rule_id}: {ev.explanation}")

        if conflicting:
            lines.append("Conflicting evidence:")
            for ev in conflicting[:3]:
                lines.append(f"  - {ev.rule_id}: {ev.explanation}")

        if not supporting and not conflicting:
            lines.append("No relevant evidence was found for the question.")

        return "\n".join(lines)
