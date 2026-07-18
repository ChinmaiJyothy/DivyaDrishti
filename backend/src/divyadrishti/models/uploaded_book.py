"""Uploaded book model for admin book ingestion."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from divyadrishti.database.database import Base


class UploadedBook(Base):
    """An astrology book uploaded by an admin for ingestion into a Knowledge Corpus."""

    __tablename__ = "uploaded_books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    corpus_id: Mapped[int | None] = mapped_column(ForeignKey("corpora.id"), nullable=True, index=True)

    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    edition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # pending, processing, completed, failed
    status: Mapped[str] = mapped_column(String(50), default="pending")
    book_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ingestion_report_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    corpus: Mapped["Corpus"] = relationship("Corpus", back_populates="books")  # noqa: F821
    candidate_rules: Mapped[list["CandidateRule"]] = relationship(  # noqa: F821
        "CandidateRule", back_populates="book"
    )
    extracted_pages: Mapped[list["ExtractedBookPage"]] = relationship(  # noqa: F821
        "ExtractedBookPage",
        back_populates="book",
        order_by="ExtractedBookPage.page_number.asc()",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
