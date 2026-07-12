"""Pydantic models for the Evidence and Rule Evaluation Engine."""

from pydantic import BaseModel, Field, computed_field


class PlanetPosition(BaseModel):
    """Position of a planet in a birth chart."""

    house: int | None = None
    sign: str | None = None
    nakshatra: str | None = None
    dignity: str | None = None
    retrograde: bool = False
    combust: bool = False


class ChartData(BaseModel):
    """Structured birth chart data used for rule evaluation."""

    planets: dict[str, PlanetPosition] = Field(default_factory=dict)
    yogas: list[str] = Field(default_factory=list)
    doshas: list[str] = Field(default_factory=list)
    dashas: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def active_houses(self) -> list[int]:
        return sorted(
            {position.house for position in self.planets.values() if position.house is not None}
        )

    @computed_field
    @property
    def active_planets(self) -> list[str]:
        return list(self.planets.keys())

    @computed_field
    @property
    def active_signs(self) -> list[str]:
        return sorted(
            {position.sign for position in self.planets.values() if position.sign}
        )

    @computed_field
    @property
    def active_nakshatras(self) -> list[str]:
        return sorted(
            {position.nakshatra for position in self.planets.values() if position.nakshatra}
        )


class Evidence(BaseModel):
    """Evaluation of a single rule against a birth chart."""

    rule_id: str
    source: str
    conditions: list[str] = Field(default_factory=list)
    matched_conditions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    weight: float = Field(default=0.0)
    match_status: str = "not_matched"
    supporting: list[str] = Field(default_factory=list)
    conflicting: list[str] = Field(default_factory=list)
    explanation: str = ""
    notes: str = ""

    def is_supporting(self) -> bool:
        return self.confidence > 0


class ReasoningTrace(BaseModel):
    """Final structured reasoning output passed to the LLM layer."""

    question: str
    domain: str = "general"
    chart_data: dict
    relevant_factors: dict = Field(default_factory=dict)
    matched_rules: list[Evidence] = Field(default_factory=list)
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    conflicting_evidence: list[Evidence] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    reasoning_summary: str = ""
    reasoning_steps: list[dict] = Field(default_factory=list)
    suggested_follow_up_topics: list[str] = Field(default_factory=list)
