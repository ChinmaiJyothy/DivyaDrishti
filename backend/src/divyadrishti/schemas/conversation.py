"""Conversation and message schemas."""

from datetime import datetime

from pydantic import BaseModel, model_validator


class ConversationCreateRequest(BaseModel):
    birth_profile_id: int | None = None
    title: str | None = None
    domain: str | None = None


class ConversationUpdateRequest(BaseModel):
    title: str | None = None
    birth_profile_id: int | None = None
    is_archived: bool | None = None
    is_pinned: bool | None = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    ai_response_json: dict | None = None
    reasoning_result: dict | None = None
    explainability_report: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_reasoning_and_explainability(cls, data):
        if not isinstance(data, dict):
            data = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}

        if data.get("reasoning_results"):
            first = data["reasoning_results"][0]
            data["reasoning_result"] = _sqlalchemy_to_dict(first)
        else:
            data["reasoning_result"] = None

        if data.get("explainability_reports"):
            first = data["explainability_reports"][0]
            data["explainability_report"] = _sqlalchemy_to_dict(first)
        else:
            data["explainability_report"] = None

        return data


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    birth_profile_id: int | None
    title: str | None
    domain: str | None
    is_archived: bool
    is_pinned: bool
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
            confidences = []
            for r in results:
                if isinstance(r, dict):
                    conf = r.get("overall_confidence")
                else:
                    conf = getattr(r, "overall_confidence", None)
                if conf is not None:
                    confidences.append(conf)
            if confidences:
                data["confidence"] = round(sum(confidences) / len(confidences), 2)
        return data


class MessageCreateRequest(BaseModel):
    role: str
    content: str
    ai_response_json: dict | None = None


def _sqlalchemy_to_dict(obj) -> dict:
    """Convert a SQLAlchemy model instance to a plain dict with JSON columns."""
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.key)
        result[column.key] = value
    return result
