"""Pydantic models for the Explainable Astrology Engine."""

from pydantic import BaseModel, Field


class Node(BaseModel):
    """A single node in a reasoning or visualization graph."""

    id: str
    label: str
    type: str = "step"
    children: list["Node"] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ReasoningGraph(BaseModel):
    """A traversable graph of reasoning steps."""

    root: Node


class RuleTrace(BaseModel):
    """Traceability data for a single rule."""

    rule_id: str
    source_book: str
    chapter: str | None = None
    verse: str | None = None
    page: str | None = None
    conditions: list[str] = Field(default_factory=list)
    matched_conditions: list[str] = Field(default_factory=list)
    weight: float = 0.0
    confidence: float = 0.0
    match_status: str = "not_matched"
    reason_included: str = ""
    reason_excluded: str = ""


class EvidenceExplanation(BaseModel):
    """Human-readable explanation for a supporting or conflicting factor."""

    factor: str
    why_it_matters: str = ""
    rule_id: str
    source: str
    confidence_impact: float = 0.0


class ConfidenceContribution(BaseModel):
    """A single contributor to the overall confidence."""

    name: str
    contribution: float
    type: str = "support"  # support or conflict


class ConfidenceBreakdown(BaseModel):
    """Overall confidence with individual contributions."""

    overall_confidence: float
    contributors: list[ConfidenceContribution] = Field(default_factory=list)


class Limitation(BaseModel):
    """A limitation of the current interpretation."""

    type: str
    description: str


class ReferenceEntry(BaseModel):
    """A classical reference for a conclusion."""

    book: str
    chapter: str | None = None
    verse: str | None = None
    page: str | None = None
    original_language: str | None = None
    translated_text: str = ""
    corpus: str | None = None
    original_text: str | None = None
    retrieval_score: float | None = None


class SuggestedReading(BaseModel):
    """Suggested classical reading for the user."""

    book: str
    chapter: str | None = None
    topic: str = ""


class VisualizationData(BaseModel):
    """Structured data for frontend visualization."""

    decision_tree: dict = Field(default_factory=dict)
    reasoning_timeline: list[dict] = Field(default_factory=list)
    evidence_tree: dict = Field(default_factory=dict)
    planet_influence_graph: dict = Field(default_factory=dict)
    house_influence_graph: dict = Field(default_factory=dict)
    knowledge_source_graph: dict = Field(default_factory=dict)


class ExplainabilityReport(BaseModel):
    """Structured explainability report for an astrological conclusion."""

    question: str
    detected_domain: str = ""
    chart_factors_used: dict = Field(default_factory=dict)
    rules_considered: list[str] = Field(default_factory=list)
    matched_rules: list[RuleTrace] = Field(default_factory=list)
    ignored_rules: list[RuleTrace] = Field(default_factory=list)
    supporting_evidence: list[EvidenceExplanation] = Field(default_factory=list)
    conflicting_evidence: list[EvidenceExplanation] = Field(default_factory=list)
    reasoning_path: ReasoningGraph | None = None
    confidence_score: ConfidenceBreakdown | None = None
    limitations: list[Limitation] = Field(default_factory=list)
    classical_references: list[ReferenceEntry] = Field(default_factory=list)
    suggested_reading: list[SuggestedReading] = Field(default_factory=list)
    important_notes: list[str] = Field(default_factory=list)
    visualizations: VisualizationData = Field(default_factory=VisualizationData)
