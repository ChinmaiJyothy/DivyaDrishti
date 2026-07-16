"""Candidate rule and review audit models for the Knowledge Corpus.

Candidate rules are extracted automatically from ingested books but
NEVER become active/usable by the Reasoning Engine until an
administrator explicitly approves them (see ``CandidateRuleStatus``).
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from divyadrishti.database.database import Base


class CandidateRuleStatus(str, Enum):
    """Lifecycle states for a candidate rule under administrator review."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    MERGED = "merged"


class CandidateRule(Base):
    """A rule candidate extracted from a corpus book, pending review."""

    __tablename__ = "candidate_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_rule_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    corpus_id: Mapped[int] = mapped_column(ForeignKey("corpora.id"), nullable=False, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("uploaded_books.id"), nullable=False, index=True)

    source_book_title: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="en")
    chapter: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verse: Mapped[str | None] = mapped_column(String(100), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    topic: Mapped[str] = mapped_column(String(100), default="general")
    subtopic: Mapped[str | None] = mapped_column(String(100), nullable=True)

    astrological_factors_json: Mapped[dict] = mapped_column(JSON, default=dict)
    candidate_conditions_json: Mapped[list] = mapped_column(JSON, default=list)
    candidate_interpretation: Mapped[str] = mapped_column(Text, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[str] = mapped_column(String(50), default=CandidateRuleStatus.PENDING.value, index=True)

    chunk_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    approved_rule_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    merged_into_candidate_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_rules.id"), nullable=True
    )

    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    version: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    corpus: Mapped["Corpus"] = relationship("Corpus", back_populates="candidate_rules")  # noqa: F821
    book: Mapped["UploadedBook"] = relationship("UploadedBook", back_populates="candidate_rules")  # noqa: F821
    audit_entries: Mapped[list["RuleReviewAudit"]] = relationship(
        "RuleReviewAudit", back_populates="candidate_rule", cascade="all, delete-orphan"
    )


class RuleReviewAudit(Base):
    """Immutable audit trail entry for every administrator action on a candidate rule."""

    __tablename__ = "rule_review_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_rule_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_rules.id"), nullable=False, index=True
    )
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    # approve | reject | merge | edit | annotate | version | compare
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    candidate_rule: Mapped["CandidateRule"] = relationship("CandidateRule", back_populates="audit_entries")
