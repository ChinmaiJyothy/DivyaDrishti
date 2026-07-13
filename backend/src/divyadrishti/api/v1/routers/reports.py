"""Report API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.report import ReportCreateRequest, ReportResponse, ReportUpdateRequest
from divyadrishti.security import get_current_user
from divyadrishti.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def _service(db: Session) -> ReportService:
    return ReportService(db)


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    body: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _service(db).create(current_user.id, body.model_dump())


@router.get("", response_model=list[ReportResponse])
def list_reports(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return _service(db).list(current_user.id)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = _service(db).get(report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.patch("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    body: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    report = service.get(report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return service.update(report, body.model_dump(exclude_unset=True))


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    report = service.get(report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    service.delete(report)
    return {"detail": "Report deleted"}
