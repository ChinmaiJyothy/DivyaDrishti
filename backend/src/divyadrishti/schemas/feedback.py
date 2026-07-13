"""Feedback schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    conversation_id: int | None = None
    message_id: int | None = None
    rating: str = Field(pattern=r"^(Very Helpful|Helpful|Neutral|Not Helpful|Incorrect)$")
    comment: str | None = None
    response_text: str | None = None
    reasoning_trace: dict[str, Any] | None = None
    rules_used: list[str] | None = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    conversation_id: int | None
    message_id: int | None
    rating: str
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
