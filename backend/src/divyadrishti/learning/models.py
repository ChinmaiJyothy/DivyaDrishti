"""Pydantic models for the learning and continuous improvement system."""

from pydantic import BaseModel, Field


class QualityMetrics(BaseModel):
    """Quality metrics for a single rule."""

    rule_id: str
    usage_count: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    conflict_frequency: int = 0
    retrieval_frequency: int = 0
    confidence_stability: float = 0.0
    quality_score: float = 0.0


class AuditEntry(BaseModel):
    """A single audit log entry."""

    timestamp: str
    action: str
    user: str
    reason: str
    affected_objects: list[str] = Field(default_factory=list)
