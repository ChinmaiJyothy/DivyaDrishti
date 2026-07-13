"""Birth chart schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BirthChartResponse(BaseModel):
    id: int
    profile_id: int
    chart_type: str
    chart_data: dict[str, Any] | None
    generated_at: datetime

    model_config = {"from_attributes": True}
