"""Pydantic models for the Birth Chart Studio API."""

from typing import Any

from pydantic import BaseModel, Field


class PlanetPosition(BaseModel):
    """A planet in a birth chart."""

    name: str
    longitude: float
    sign: str
    sign_degree: float
    house: int
    nakshatra: str
    nakshatra_pada: int
    nakshatra_lord: str
    dignity: str
    retrograde: bool
    combust: bool
    degree: float
    lord: str | None = None  # sign lord
    navamsa_sign: str | None = None
    navamsa_house: int | None = None
    navamsa_degree: float | None = None
    aspects: list[str] = Field(default_factory=list)  # planet names
    conjunctions: list[str] = Field(default_factory=list)  # planet names


class HousePosition(BaseModel):
    """A house in a birth chart."""

    house: int
    sign: str
    lord: str
    planets: list[str] = Field(default_factory=list)
    aspected_by: list[str] = Field(default_factory=list)
    meaning: str
    trinity: str
    is_kendra: bool
    is_upachaya: bool
    is_malefic: bool
    is_benefic: bool


class NakshatraDetail(BaseModel):
    """Detailed nakshatra info for a planet."""

    name: str
    pada: int
    lord: str
    planet: str
    longitude: float
    characteristics: str = Field(default="")
    current_influence: str = Field(default="")


class DashaPeriod(BaseModel):
    """A single Vimshottari dasha period."""

    planet: str
    start_date: str
    end_date: str
    is_current: bool
    major_themes: list[str] = Field(default_factory=list)
    relevant_planets: list[str] = Field(default_factory=list)


class YogaDetail(BaseModel):
    """Detected yoga in a chart."""

    name: str
    strength: str
    description: str
    conditions: list[str] = Field(default_factory=list)
    matched_conditions: list[str] = Field(default_factory=list)
    current_relevance: str = Field(default="")
    references: list[str] = Field(default_factory=list)


class DoshaDetail(BaseModel):
    """Detected dosha in a chart."""

    name: str
    severity: str
    conditions: list[str] = Field(default_factory=list)
    mitigating_factors: list[str] = Field(default_factory=list)
    confidence: float
    references: list[str] = Field(default_factory=list)


class AspectDetail(BaseModel):
    """A planetary aspect relationship."""

    source: str
    target: str
    aspect_houses: list[int]
    orb: float
    type: str


class TransitPosition(BaseModel):
    """Current transiting position of a planet."""

    name: str
    sign: str
    house: int
    longitude: float
    nakshatra: str
    retrograde: bool


class ChartData(BaseModel):
    """Core chart data for a birth chart."""

    chart_type: str
    lagna: str
    lagna_degree: float
    lagna_nakshatra: str
    moon_sign: str
    sun_sign: str
    maha_dasha: str
    antar_dasha: str
    planets: dict[str, PlanetPosition]
    houses: dict[str, HousePosition]  # keyed as str(house)
    nakshatras: dict[str, NakshatraDetail]
    dashas: list[DashaPeriod]
    yogas: list[YogaDetail]
    doshas: list[DoshaDetail]
    aspects: list[AspectDetail]
    transits: list[TransitPosition]
    generated_at: str


class VargaChart(BaseModel):
    """A divisional chart."""

    chart_type: str
    lagna: str
    lagna_degree: float
    planets: dict[str, PlanetPosition]
    houses: dict[str, HousePosition]


class InsightHighlight(BaseModel):
    """A single highlighted element for the insight panel."""

    type: str  # planet, house, sign, yoga, dosha, dasha
    id: str
    label: str
    reason: str
    strength: str | None = None


class StudioInsight(BaseModel):
    """Context-aware insight for a chart and question/topic."""

    topic: str
    highlights: list[InsightHighlight]
    summary: str
    recommendations: list[str] = Field(default_factory=list)


class ChartStudioDetail(BaseModel):
    """Full studio payload for a birth chart."""

    chart_id: int
    profile_id: int
    chart_type: str
    lagna: str
    lagna_degree: float
    moon_sign: str
    sun_sign: str
    maha_dasha: str
    antar_dasha: str
    planets: dict[str, PlanetPosition]
    houses: dict[str, HousePosition]
    nakshatras: dict[str, NakshatraDetail]
    dashas: list[DashaPeriod]
    yogas: list[YogaDetail]
    doshas: list[DoshaDetail]
    aspects: list[AspectDetail]
    transits: list[TransitPosition]
    visualizations: dict[str, Any]
    insight: StudioInsight | None = None
    generated_at: str
