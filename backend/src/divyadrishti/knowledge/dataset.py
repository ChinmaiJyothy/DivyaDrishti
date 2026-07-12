"""Export supervised fine-tuning datasets from structured knowledge."""

import json
from pathlib import Path

from divyadrishti.knowledge.models import Rule, TrainingEntry


class TrainingDatasetExporter:
    """Generate training examples for future LLM fine-tuning.

    Each example links a birth chart, a question, the relevant rules,
    reasoning steps, and source references.
    """

    def export(self, entries: list[TrainingEntry], output: Path | str) -> Path:
        """Export a list of training entries to a JSONL file."""
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry.model_dump(), ensure_ascii=False) + "\n")
        return output_path

    def build_entry(
        self,
        chart: dict,
        question: str,
        rules: list[Rule],
        reasoning_steps: list[str],
        final_answer: str,
    ) -> TrainingEntry:
        """Build a single training example from the reasoning pipeline."""
        return TrainingEntry(
            birth_chart=chart,
            question=question,
            relevant_rules=[rule.model_dump() for rule in rules],
            reasoning_steps=reasoning_steps,
            final_answer=final_answer,
            source_references=[rule.citation().model_dump() for rule in rules],
        )

    def build_from_rule(
        self,
        rule: Rule,
        chart: dict | None = None,
        question: str | None = None,
        final_answer: str | None = None,
    ) -> TrainingEntry:
        """Build a minimal training example from a single rule."""
        return TrainingEntry(
            birth_chart=chart or {},
            question=question or f"Tell me about {rule.topic}",
            relevant_rules=[rule.model_dump()],
            reasoning_steps=[
                f"Identify {rule.topic} in the chart",
                f"Check condition: {'; '.join(rule.conditions)}",
                rule.interpretation,
            ],
            final_answer=final_answer or rule.interpretation,
            source_references=[rule.citation().model_dump()],
        )
