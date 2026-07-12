"""Feedback Manager for collecting and storing user feedback."""

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class FeedbackEntry(BaseModel):
    """A single user feedback item."""

    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    question: str
    reasoning_trace: dict[str, Any]
    rules_used: list[str] = Field(default_factory=list)
    response: str
    rating: str
    comment: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


VALID_RATINGS = {"Very Helpful", "Helpful", "Neutral", "Not Helpful", "Incorrect"}


class FeedbackManager:
    """Collect, store, and query user feedback."""

    def __init__(self) -> None:
        self.feedback: list[FeedbackEntry] = []

    def add(self, entry: FeedbackEntry) -> None:
        """Add a feedback entry."""
        if entry.rating not in VALID_RATINGS:
            raise ValueError(f"Invalid rating: {entry.rating}")
        self.feedback.append(entry)

    def for_rule(self, rule_id: str) -> list[FeedbackEntry]:
        """Return feedback linked to a specific rule."""
        return [f for f in self.feedback if rule_id in f.rules_used]

    def summary(self) -> dict[str, int]:
        """Aggregate ratings."""
        counts = {rating: 0 for rating in VALID_RATINGS}
        for entry in self.feedback:
            counts[entry.rating] = counts.get(entry.rating, 0) + 1
        return counts

    def export(self) -> list[dict[str, Any]]:
        """Export all feedback entries."""
        return [entry.model_dump() for entry in self.feedback]
