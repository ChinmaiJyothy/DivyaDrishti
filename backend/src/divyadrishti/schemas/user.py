"""User and profile schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str | None = None
    is_verified: bool
    is_active: bool
    account_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_role(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            data = {
                k: v
                for k, v in data.__dict__.items()
                if not k.startswith("_")
            }
        role = data.get("role")
        if role and hasattr(role, "name"):
            data["role"] = role.name
        return data


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    preferred_language: str | None = None
    timezone: str | None = None
    country: str | None = None
    theme_preference: str | None = None
    notification_settings: dict[str, Any] | None = None
    privacy_settings: dict[str, Any] | None = None
