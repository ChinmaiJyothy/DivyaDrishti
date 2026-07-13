"""User preference schemas."""

from pydantic import BaseModel


class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    preferred_language: str
    preferred_explanation_depth: str
    preferred_astrology_school: str
    preferred_chart_style: str
    citation_mode: str
    dark_mode: bool
    units: str
    timezone: str
    country: str | None
    theme_preference: str

    model_config = {"from_attributes": True}


class PreferenceUpdateRequest(BaseModel):
    preferred_language: str | None = None
    preferred_explanation_depth: str | None = None
    preferred_astrology_school: str | None = None
    preferred_chart_style: str | None = None
    citation_mode: str | None = None
    dark_mode: bool | None = None
    units: str | None = None
    timezone: str | None = None
    country: str | None = None
    theme_preference: str | None = None
