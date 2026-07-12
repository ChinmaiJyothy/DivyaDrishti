"""Pydantic models for the Vedic astrology knowledge base."""

from pydantic import BaseModel, Field, field_validator, model_validator

from divyadrishti.knowledge.constants import (
    VALID_BOOKS,
    VALID_DASHAS,
    VALID_DOSHAS,
    VALID_HOUSES,
    VALID_NAKSHATRAS,
    VALID_PLANETS,
    VALID_SIGNS,
    VALID_YOGAS,
)


def _parse_list(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        return [
            item.strip().strip('"').strip("'")
            for item in value.split(",")
            if item.strip()
        ]
    return value


def _parse_houses(value: str | list[int]) -> list[int]:
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        return [int(item.strip()) for item in value.split(",") if item.strip()]
    return value


class AstrologicalFactors(BaseModel):
    """Structured astrological factors referenced by a rule."""

    houses: list[int] = Field(default_factory=list)
    planets: list[str] = Field(default_factory=list)
    signs: list[str] = Field(default_factory=list)
    nakshatras: list[str] = Field(default_factory=list)
    yogas: list[str] = Field(default_factory=list)
    doshas: list[str] = Field(default_factory=list)
    dashas: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)

    @field_validator("houses", mode="before")
    @classmethod
    def parse_houses(cls, value: str | list[int]) -> list[int]:
        return _parse_houses(value)

    @field_validator("planets", "signs", "nakshatras", "yogas", "doshas", "dashas", "topics", mode="before")
    @classmethod
    def parse_lists(cls, value: str | list[str]) -> list[str]:
        return _parse_list(value)


class Citation(BaseModel):
    """Traceable citation for a rule."""

    rule_id: str
    source_book: str
    chapter: str | None = None
    verse: str | None = None
    references: list[str] = Field(default_factory=list)


class Rule(BaseModel):
    """A single, machine-readable Vedic astrology rule."""

    rule_id: str = Field(..., pattern=r"^[A-Z][A-Z0-9_]*$")
    source_book: str
    chapter: str | None = None
    verse: str | None = None
    topic: str
    subtopic: str | None = None
    category: str
    conditions: list[str] = Field(default_factory=list)
    astrological_factors: AstrologicalFactors = Field(default_factory=AstrologicalFactors)
    interpretation: str
    supporting_notes: str | None = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    enabled: bool = True

    @field_validator("conditions", "references", "tags", mode="before")
    @classmethod
    def parse_string_lists(cls, value: str | list[str]) -> list[str]:
        return _parse_list(value)

    @model_validator(mode="after")
    def check_source_book(self) -> "Rule":
        if self.source_book not in VALID_BOOKS and self.source_book not in VALID_BOOKS.values():
            raise ValueError(f"Unknown source book: {self.source_book}")
        return self

    def citation(self) -> Citation:
        return Citation(
            rule_id=self.rule_id,
            source_book=self.source_book,
            chapter=self.chapter,
            verse=self.verse,
            references=self.references,
        )

    def summary(self) -> str:
        return f"{self.rule_id}: {self.interpretation[:100]}"


class Book(BaseModel):
    """Metadata for a classical Vedic astrology text."""

    book_id: str = Field(..., pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    title: str
    author: str | None = None
    language: str | None = None
    period: str | None = None
    source_url: str | None = None
    description: str | None = None
    chapters: dict[str, str] = Field(default_factory=dict)


class ReasoningInput(BaseModel):
    """Input provided to the Reasoning Engine."""

    chart: dict
    question: str
    relevant_rules: list[Rule] = Field(default_factory=list)
    conversation_context: list[dict] = Field(default_factory=list)


class TrainingEntry(BaseModel):
    """A single supervised fine-tuning example."""

    birth_chart: dict
    question: str
    relevant_rules: list[dict]
    reasoning_steps: list[str]
    final_answer: str
    source_references: list[dict]
