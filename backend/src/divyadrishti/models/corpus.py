"""Knowledge Corpus model.

A Corpus is a first-class grouping of source books, chapters, verses,
rules, embeddings, and knowledge-graph nodes that share a common
lineage (e.g. "Classical Vedic Astrology", "Jaimini Corpus", "KP Corpus").

The Reasoning Engine and the hybrid retrieval engine can be scoped to
one or more corpora, allowing multiple schools of astrology to coexist
without polluting each other's rule sets.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from divyadrishti.database.database import Base


class Corpus(Base):
    """A named collection of astrological source material."""

    __tablename__ = "corpora"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    corpus_type: Mapped[str] = mapped_column(String(50), default="classical")
    # classical | jaimini | kp | research | user | other
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    authority_weight: Mapped[float] = mapped_column(default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    books: Mapped[list["UploadedBook"]] = relationship(  # noqa: F821
        "UploadedBook", back_populates="corpus"
    )
    candidate_rules: Mapped[list["CandidateRule"]] = relationship(  # noqa: F821
        "CandidateRule", back_populates="corpus"
    )
