"""Knowledge Corpus API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.reasoning.astrological.models import AstrologicalEntity


class CorpusCreateRequest(BaseModel):
    slug: str
    name: str
    corpus_type: str = "classical"
    description: str | None = None
    authority_weight: float = 1.0


class CorpusResponse(BaseModel):
    id: int
    slug: str
    name: str
    corpus_type: str
    description: str | None
    authority_weight: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BookUploadMetadataRequest(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    edition: str | None = None
    isbn: str | None = None
    publication_year: int | None = None
    source: str | None = None
    language_hint: str | None = None


class CorpusBookResponse(BaseModel):
    id: int
    corpus_id: int | None
    title: str | None
    author: str | None
    publisher: str | None
    edition: str | None
    isbn: str | None
    publication_year: int | None
    source: str | None
    language: str | None
    status: str
    ingestion_report_json: dict[str, Any] | None
    processed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateRuleResponse(BaseModel):
    id: int
    candidate_rule_id: str
    corpus_id: int
    book_id: int
    source_book_title: str
    language: str
    chapter: str | None
    verse: str | None
    page: int | None
    original_text: str
    translated_text: str | None
    topic: str
    subtopic: str | None
    astrological_factors_json: dict[str, Any]
    candidate_conditions_json: list[str]
    candidate_interpretation: str
    confidence: float
    status: str
    approved_rule_id: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None
    review_notes: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateRuleEditRequest(BaseModel):
    topic: str | None = None
    subtopic: str | None = None
    candidate_interpretation: str | None = None
    candidate_conditions: list[str] | None = None
    confidence: float | None = None
    notes: str | None = None


class CandidateRuleActionRequest(BaseModel):
    notes: str | None = None


class CandidateRuleMergeRequest(BaseModel):
    target_candidate_id: int
    notes: str | None = None


class CandidateRuleAnnotationRequest(BaseModel):
    comment: str


class RuleReviewAuditResponse(BaseModel):
    id: int
    candidate_rule_id: int
    actor_id: int | None
    action: str
    comment: str | None
    previous_state_json: dict[str, Any] | None
    new_state_json: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateRuleCompareResponse(BaseModel):
    left: CandidateRuleResponse
    right: CandidateRuleResponse
    differences: dict[str, dict[str, Any]]


class GraphTraversalResponse(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)


class CorpusRetrieveRequest(BaseModel):
    question: str
    entities: AstrologicalEntity = Field(default_factory=AstrologicalEntity)
    corpus_ids: list[int] | None = None
    n_results: int = 8
