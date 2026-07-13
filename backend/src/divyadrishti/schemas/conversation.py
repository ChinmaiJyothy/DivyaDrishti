"""Conversation and message schemas."""

from datetime import datetime

from pydantic import BaseModel, model_validator


class ConversationCreateRequest(BaseModel):
    birth_profile_id: int | None = None
    title: str | None = None
    domain: str | None = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    birth_profile_id: int | None
    title: str | None
    domain: str | None
    is_archived: bool
    is_deleted: bool
    confidence: float | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_confidence(cls, data):
        if not isinstance(data, dict):
            data = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}

        results = []
        reasoning_results = data.get("reasoning_results")
        if reasoning_results:
            results = reasoning_results
        elif data.get("messages"):
            for msg in data.get("messages", []):
                if hasattr(msg, "reasoning_results"):
                    results.extend(msg.reasoning_results)

        if results:
            confidences = [
                getattr(r, "overall_confidence", r.get("overall_confidence"))
                for r in results
                if getattr(r, "overall_confidence", r.get("overall_confidence")) is not None
            ]
            if confidences:
                data["confidence"] = round(sum(confidences) / len(confidences), 2)
        return data


class MessageCreateRequest(BaseModel):
    role: str
    content: str
    ai_response_json: dict | None = None
