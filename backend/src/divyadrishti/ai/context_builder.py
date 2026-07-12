"""Context Builder for the AI Conversation Engine."""

import json
from typing import Any

from divyadrishti.ai.memory import ConversationMemory


class ContextBuilder:
    """Build a conversation context prompt from reasoning, memory, and preferences."""

    def __init__(self, max_chars: int = 12000) -> None:
        self.max_chars = max_chars

    def build(
        self,
        question: str,
        reasoning: dict[str, Any],
        memory: ConversationMemory | None = None,
        chart_summary: str = "",
        language: str = "en",
    ) -> str:
        """Build a full user prompt for the LLM."""
        memory = memory or ConversationMemory()
        sections = [
            self._section("Preferred Language", language),
            self._section("User Question", question),
            self._section("Chart Summary", chart_summary),
            self._section("Reasoning Result", self._render_reasoning(reasoning)),
            self._section("Matched Rules", self._render_list(reasoning.get("matched_rules", []))),
            self._section(
                "Supporting Evidence", self._render_list(reasoning.get("supporting_evidence", []))
            ),
            self._section(
                "Conflicting Evidence", self._render_list(reasoning.get("conflicting_evidence", []))
            ),
            self._section("Confidence Score", str(reasoning.get("overall_confidence", "N/A"))),
            self._section("Conversation History", self._render_history(memory.get_history())),
            self._section("User Preferences", self._render_preferences(memory.preferences)),
            self._section(
                "Source References",
                self._render_list(reasoning.get("references", [])),
            ),
        ]

        context = "\n\n".join(sections)
        return self._truncate(context)

    def _section(self, title: str, content: str) -> str:
        return f"### {title}\n{content}"

    def _render_reasoning(self, reasoning: dict[str, Any]) -> str:
        return json.dumps(reasoning, indent=2, ensure_ascii=False, default=str)

    def _render_list(self, items: list[Any]) -> str:
        if not items:
            return "None"
        return "\n".join(f"- {self._summarize(item)}" for item in items)

    def _summarize(self, item: Any) -> str:
        if isinstance(item, dict):
            return item.get("rule_id", item.get("source", str(item)))
        return str(item)

    def _render_history(self, history: list[dict[str, str]]) -> str:
        if not history:
            return "No prior conversation."
        return "\n".join(
            f"{entry.get('role', 'user')}: {entry.get('content', '')}" for entry in history
        )

    def _render_preferences(self, preferences: dict[str, Any]) -> str:
        return json.dumps(preferences, indent=2, ensure_ascii=False, default=str)

    def _truncate(self, text: str) -> str:
        if len(text) <= self.max_chars:
            return text

        # Truncate from the middle, keeping question and reasoning summary intact.
        lines = text.split("\n")
        total = 0
        kept = []
        for line in lines:
            if total + len(line) > self.max_chars:
                break
            kept.append(line)
            total += len(line) + 1

        kept.append("\n[Context truncated to fit model limits.]")
        return "\n".join(kept)
