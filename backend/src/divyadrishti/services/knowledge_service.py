"""Knowledge library service."""

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from divyadrishti.models import UploadedBook
from divyadrishti.repositories import KnowledgeVersionRepository, UploadedBookRepository

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "books"


class KnowledgeService:
    """Admin knowledge library operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.book_repo = UploadedBookRepository(db)
        self.version_repo = KnowledgeVersionRepository(db)

    def list_books(self) -> list[UploadedBook]:
        return self.book_repo.list_all()

    async def create_book(
        self,
        user_id: int,
        file: UploadFile,
        title: str | None,
        author: str | None,
        language: str | None,
    ) -> UploadedBook:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        file_name = file.filename or "uploaded_book"
        file_path = UPLOADS_DIR / file_name
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())

        book = UploadedBook(
            user_id=user_id,
            file_path=str(file_path),
            file_name=file_name,
            title=title or file_name,
            author=author,
            language=language,
            status="pending",
        )
        return self.book_repo.create(book)

    def delete_book(self, book_id: int) -> None:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        self.book_repo.delete(book)

    def list_versions(self) -> list:
        return self.version_repo.list_all()

    def overview(self) -> dict:
        books = self.book_repo.list_all()
        versions = self.version_repo.list_all()
        latest_version = self.version_repo.get_latest()
        return {
            "books_count": len(books),
            "versions_count": len(versions),
            "last_updated": latest_version.modified_at.isoformat() if latest_version else None,
        }
