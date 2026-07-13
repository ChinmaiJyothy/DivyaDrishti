"""Knowledge library schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BookResponse(BaseModel):
    id: int
    user_id: int
    file_path: str
    file_name: str
    title: str | None
    author: str | None
    language: str | None
    status: str
    book_metadata: dict[str, Any] | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BookCreateRequest(BaseModel):
    title: str | None = None
    author: str | None = None
    language: str | None = None


class KnowledgeVersionResponse(BaseModel):
    id: int
    rule_id: str
    version: str
    created_at: datetime
    modified_at: datetime
    modified_by: str | None
    approval_status: str
    change_history: str | None
    deprecated: bool

    model_config = {"from_attributes": True}


class KnowledgeOverviewResponse(BaseModel):
    books_count: int
    versions_count: int
    last_updated: str | None
