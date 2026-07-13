"""Uploaded book repository."""

from sqlalchemy.orm import Session

from divyadrishti.models import UploadedBook


class UploadedBookRepository:
    """Database operations for uploaded books."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[UploadedBook]:
        return (
            self.db.query(UploadedBook)
            .filter(UploadedBook.is_active.is_(True))
            .order_by(UploadedBook.created_at.desc())
            .all()
        )

    def get_by_id(self, book_id: int) -> UploadedBook | None:
        return (
            self.db.query(UploadedBook)
            .filter(UploadedBook.id == book_id, UploadedBook.is_active.is_(True))
            .first()
        )

    def create(self, book: UploadedBook) -> UploadedBook:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: UploadedBook) -> None:
        self.db.delete(book)
        self.db.commit()
