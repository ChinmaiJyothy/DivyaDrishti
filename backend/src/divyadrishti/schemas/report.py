"""Report schemas."""

from datetime import datetime

from pydantic import BaseModel


class ReportCreateRequest(BaseModel):
    title: str
    category: str


class ReportUpdateRequest(BaseModel):
    title: str | None = None
    category: str | None = None
    status: str | None = None
    file_url: str | None = None
    file_name: str | None = None


class ReportResponse(BaseModel):
    id: int
    user_id: int
    title: str
    category: str
    status: str
    file_url: str | None
    file_name: str | None
    file_format: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
