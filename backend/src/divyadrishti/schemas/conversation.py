"""Conversation and message schemas."""

from datetime import datetime

from pydantic import BaseModel


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
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class MessageCreateRequest(BaseModel):
    role: str
    content: str
    ai_response_json: dict | None = None
