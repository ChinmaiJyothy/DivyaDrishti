"""Extracted book page model for storing raw, per-page book text."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from divyadrishti.database.database import Base


class ExtractedBookPage(Base):
    """A single page of extracted text from an uploaded book."""

    __tablename__ = "extracted_book_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("uploaded_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    book: Mapped["UploadedBook"] = relationship("UploadedBook", back_populates="extracted_pages")  # noqa: F821

    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    chapter: Mapped[str | None] = mapped_column(String(255), nullable=True)
    section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verse: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
