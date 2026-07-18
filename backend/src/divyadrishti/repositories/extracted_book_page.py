"""Repository for extracted book pages."""

from sqlalchemy.orm import Session

from divyadrishti.models import ExtractedBookPage


class ExtractedBookPageRepository:
    """Database operations for extracted book pages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, pages: list[ExtractedBookPage]) -> list[ExtractedBookPage]:
        """Insert multiple extracted pages and refresh them."""
        self.db.add_all(pages)
        self.db.commit()
        for page in pages:
            self.db.refresh(page)
        return pages

    def list_by_book(self, book_id: int) -> list[ExtractedBookPage]:
        """Return all extracted pages for a book, ordered by page number."""
        return (
            self.db.query(ExtractedBookPage)
            .filter(ExtractedBookPage.book_id == book_id)
            .order_by(ExtractedBookPage.page_number.asc())
            .all()
        )
