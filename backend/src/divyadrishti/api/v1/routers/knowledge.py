"""Knowledge library API routes (admin only)."""

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.knowledge import (
    BookResponse,
    KnowledgeOverviewResponse,
    KnowledgeVersionResponse,
)
from divyadrishti.security import get_current_user, require_admin
from divyadrishti.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
books_router = APIRouter(prefix="/books", tags=["books"])


def _service(db: Session) -> KnowledgeService:
    return KnowledgeService(db)


@books_router.get("", response_model=list[BookResponse])
def list_books(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(db).list_books()


@books_router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def upload_book(
    file: UploadFile,
    title: str | None = Form(None),
    author: str | None = Form(None),
    language: str | None = Form(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await _service(db).create_book(current_user.id, file, title, author, language)


@books_router.delete("/{book_id}")
def delete_book(
    book_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        _service(db).delete_book(book_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"detail": "Book deleted"}


@router.get("/versions", response_model=list[KnowledgeVersionResponse])
def list_versions(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(db).list_versions()


@router.get("", response_model=KnowledgeOverviewResponse)
def knowledge_overview(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(db).overview()


@router.get("/books", response_model=list[BookResponse])
def list_books_alias(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(db).list_books()
