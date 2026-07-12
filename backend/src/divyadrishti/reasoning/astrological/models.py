"""Pydantic models for the Astrological Reasoning Engine."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.reasoning.models import ChartData, Evidence


class MatchStatus(str, Enum):
    """Evaluation status of a rule against a chart."""

    FULL = "matched"
    PARTIAL = "partially_matched"
    NONE = "not_matched"


class AstrologicalEntity(BaseModel):
    """A set of astrological entities relevant to a question."""

    houses: list[int] = Field(default_factory=list)
    planets: list[str] = Field(default_factory=list)
    signs: list[str] = Field(default_factory=list)
    nakshatras: list[str] = Field(default_factory=list)
    yogas: list[str] = Field(default_factory=list)
    doshas: list[str] = Field(default_factory=list)
    dashas: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class AstrologicalChart(BaseModel):
    """Complete birth chart for reasoning."""

    lagna: str = ""
    moon_sign: str = ""
    sun_sign: str = ""
    maha_dasha: str = ""
    antar_dasha: str = ""
    planets: dict[str, dict[str, Any]] = Field(default_factory=dict)
    navamsa: dict[str, dict[str, Any]] = Field(default_factory=dict)
    nakshatras: dict[str, str] = Field(default_factory=dict)
    yogas: list[str] = Field(default_factory=list)
    doshas: list[str] = Field(default_factory=list)

    def to_chart_data(self) -> ChartData:
        """Convert to ChartData used by the Evidence Engine."""
        positions = {}
        for planet, data in self.planets.items():
            positions[planet] = {
                "house": data.get("house"),
                "sign": data.get("sign"),
                "nakshatra": data.get("nakshatra"),
                "dignity": data.get("dignity"),
                "retrograde": data.get("retrograde", False),
                "combust": data.get("combust", False),
            }

        dashas = []
        if self.maha_dasha:
            dashas.append(self.maha_dasha)
        if self.antar_dasha:
            dashas.append(self.antar_dasha)

        return ChartData(
            planets=positions,
            yogas=self.yogas,
            doshas=self.doshas,
            dashas=dashas,
            topics=[],
        )


class ReasoningRequest(BaseModel):
    """Input request for the Astrological Reasoning Engine."""

    question: str
    chart: AstrologicalChart
    context: list[dict[str, Any]] = Field(default_factory=list)


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain."""

    step: str
    details: str
    evidence: list[str] = Field(default_factory=list)


class ReasoningResult(BaseModel):
    """Final structured astrological reasoning output."""

    question: str
    domain: str
    relevant_factors: AstrologicalEntity
    matched_rules: list[Evidence] = Field(default_factory=list)
    partially_matched_rules: list[Evidence] = Field(default_factory=list)
    unmatched_rules: list[Evidence] = Field(default_factory=list)
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    conflicting_evidence: list[Evidence] = Field(default_factory=list)
    overall_confidence: float = 0.0
    reasoning_summary: str = ""
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
    suggested_follow_up_topics: list[str] = Field(default_factory=list)
