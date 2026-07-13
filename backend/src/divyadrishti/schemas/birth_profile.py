"""Birth profile schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BirthProfileCreateRequest(BaseModel):
    profile_name: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    date_of_birth: str
    time_of_birth: str | None = None
    birth_place: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "UTC"
    accuracy_level: str = "exact"
    notes: str | None = None
    chart_metadata: dict[str, Any] | None = None


class BirthProfileUpdateRequest(BaseModel):
    profile_name: str | None = None
    relationship: str | None = None
    date_of_birth: str | None = None
    time_of_birth: str | None = None
    birth_place: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    accuracy_level: str | None = None
    notes: str | None = None


class BirthProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_name: str
    relationship: str
    date_of_birth: str
    time_of_birth: str | None
    birth_place: str | None
    latitude: float | None
    longitude: float | None
    timezone: str
    accuracy_level: str
    notes: str | None
    chart_metadata: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
