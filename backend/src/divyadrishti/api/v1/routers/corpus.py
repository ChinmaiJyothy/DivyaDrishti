"""Knowledge Corpus API routes (admin only)."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.knowledge.repository import KnowledgeRepository
from divyadrishti.models import User
from divyadrishti.schemas.corpus import (
    CandidateRuleActionRequest,
    CandidateRuleAnnotationRequest,
    CandidateRuleCompareResponse,
    CandidateRuleEditRequest,
    CandidateRuleMergeRequest,
    CandidateRuleResponse,
    CorpusBookResponse,
    CorpusCreateRequest,
    CorpusResponse,
    GraphTraversalResponse,
    RuleReviewAuditResponse,
)
from divyadrishti.security import get_current_user, require_admin
from divyadrishti.services.corpus_service import CorpusIngestionError, CorpusService

router = APIRouter(prefix="/corpus", tags=["knowledge-corpus"])


def _service(request: Request, db: Session) -> CorpusService:
    knowledge_repository: KnowledgeRepository | None = getattr(
        request.app.state, "knowledge_repository", None
    )
    return CorpusService(db, knowledge_repository=knowledge_repository)


# ----------------------------------------------------------------------
# Corpora
# ----------------------------------------------------------------------
@router.get("/corpora", response_model=list[CorpusResponse])
def list_corpora(
    request: Request,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(request, db).list_corpora()


@router.post("/corpora", response_model=CorpusResponse, status_code=status.HTTP_201_CREATED)
def create_corpus(
    request: Request,
    body: CorpusCreateRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(request, db).create_corpus(body.model_dump())


# ----------------------------------------------------------------------
# Books
# ----------------------------------------------------------------------
@router.post("/corpora/{corpus_id}/books", response_model=CorpusBookResponse, status_code=status.HTTP_201_CREATED)
async def upload_book(
    request: Request,
    corpus_id: int,
    file: UploadFile,
    title: str | None = Form(None),
    author: str | None = Form(None),
    publisher: str | None = Form(None),
    edition: str | None = Form(None),
    isbn: str | None = Form(None),
    publication_year: int | None = Form(None),
    source: str | None = Form(None),
    language_hint: str | None = Form(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    metadata = {
        "title": title,
        "author": author,
        "publisher": publisher,
        "edition": edition,
        "isbn": isbn,
        "publication_year": publication_year,
        "source": source,
        "language_hint": language_hint,
    }
    return await _service(request, db).upload_book(current_user.id, corpus_id, file, metadata)


@router.post("/books/{book_id}/ingest")
def ingest_book(
    request: Request,
    book_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        report = _service(request, db).ingest_book(book_id)
    except CorpusIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return report


@router.get("/books", response_model=list[CorpusBookResponse])
def list_books(
    request: Request,
    corpus_id: int | None = None,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(request, db).list_books(corpus_id=corpus_id)


@router.delete("/books/{book_id}")
def delete_book(
    request: Request,
    book_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        _service(request, db).delete_book(book_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"detail": "Book deleted"}


# ----------------------------------------------------------------------
# Candidate rule review workflow
# ----------------------------------------------------------------------
@router.get("/candidate-rules", response_model=list[CandidateRuleResponse])
def list_candidate_rules(
    request: Request,
    corpus_id: int | None = None,
    book_id: int | None = None,
    status_filter: str | None = None,
    topic: str | None = None,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(request, db).list_candidate_rules(
        corpus_id=corpus_id, book_id=book_id, status=status_filter, topic=topic
    )


@router.get("/candidate-rules/{candidate_id}", response_model=CandidateRuleResponse)
def get_candidate_rule(
    request: Request,
    candidate_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    candidate = _service(request, db).get_candidate_rule(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate rule not found")
    return candidate


@router.post("/candidate-rules/{candidate_id}/approve", response_model=CandidateRuleResponse)
def approve_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).approve_candidate_rule(candidate_id, current_user.id, body.notes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/candidate-rules/{candidate_id}/reject", response_model=CandidateRuleResponse)
def reject_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).reject_candidate_rule(candidate_id, current_user.id, body.notes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/candidate-rules/{candidate_id}/deprecate", response_model=CandidateRuleResponse)
def deprecate_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).deprecate_candidate_rule(candidate_id, current_user.id, body.notes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/candidate-rules/{candidate_id}/merge", response_model=CandidateRuleResponse)
def merge_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleMergeRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).merge_candidate_rule(
            candidate_id, body.target_candidate_id, current_user.id, body.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/candidate-rules/{candidate_id}", response_model=CandidateRuleResponse)
def edit_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleEditRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).edit_candidate_rule(
            candidate_id, current_user.id, body.model_dump(exclude_unset=True), body.notes
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/candidate-rules/{candidate_id}/annotate", response_model=RuleReviewAuditResponse)
def annotate_candidate_rule(
    request: Request,
    candidate_id: int,
    body: CandidateRuleAnnotationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).annotate_candidate_rule(candidate_id, current_user.id, body.comment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/candidate-rules/{candidate_id}/versions", response_model=list[RuleReviewAuditResponse])
def get_candidate_rule_versions(
    request: Request,
    candidate_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _service(request, db).get_audit_trail(candidate_id)


@router.get("/candidate-rules/{left_id}/compare/{right_id}", response_model=CandidateRuleCompareResponse)
def compare_candidate_rules(
    request: Request,
    left_id: int,
    right_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return _service(request, db).compare_candidate_rules(left_id, right_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ----------------------------------------------------------------------
# Knowledge graph
# ----------------------------------------------------------------------
@router.get("/graph", response_model=GraphTraversalResponse)
def traverse_graph(
    request: Request,
    node_type: str,
    ref_id: str,
    depth: int = 2,
    corpus_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _service(request, db).traverse_graph(node_type, ref_id, depth=depth, corpus_id=corpus_id)
