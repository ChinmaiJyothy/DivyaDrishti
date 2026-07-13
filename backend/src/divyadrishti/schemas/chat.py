"""Chat and streaming API schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    content: str = Field(min_length=1)
    language: str = "en"
    message_id: int | None = None


class ChatUserEvent(BaseModel):
    event: str = "user"
    message_id: int
    role: str
    content: str


class ChatDeltaEvent(BaseModel):
    event: str = "delta"
    content: str


class ChatMetadataEvent(BaseModel):
    event: str = "metadata"
    message_id: int
    ai_response: dict | None = None
    reasoning_result: dict | None = None
    explainability_report: dict | None = None
    follow_up_questions: list[str] = []
    confidence: float | None = None


class ChatErrorEvent(BaseModel):
    event: str = "error"
    detail: str


class ChatDoneEvent(BaseModel):
    event: str = "done"
