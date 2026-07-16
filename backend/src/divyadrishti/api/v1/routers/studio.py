"""Interactive Birth Chart Studio API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from divyadrishti.astrology.models import ChartStudioDetail, StudioInsight
from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.birth_chart import BirthChartResponse
from divyadrishti.security import get_current_user
from divyadrishti.services.birth_chart_service import BirthChartService
from divyadrishti.services.studio_service import StudioService

router = APIRouter(prefix="/charts", tags=["birth chart studio"])


def _chart_service(db: Session) -> BirthChartService:
    return BirthChartService(db)


def _studio_service(db: Session, request: Request) -> StudioService:
    knowledge_repository = getattr(request.app.state, "knowledge_repository", None)
    return StudioService(db, knowledge_repository)


@router.get("/{chart_id}", response_model=BirthChartResponse)
def get_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BirthChartResponse:
    chart = _chart_service(db).get_by_id(chart_id, current_user.id)
    if not chart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
    return chart


@router.get("/{chart_id}/studio", response_model=ChartStudioDetail)
def get_studio(
    chart_id: int,
    request: Request,
    question: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChartStudioDetail:
    service = _studio_service(db, request)
    try:
        return service.get_studio_detail(chart_id, current_user.id, question)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{chart_id}/analyze", response_model=StudioInsight)
def analyze_chart(
    chart_id: int,
    request: Request,
    question: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioInsight:
    service = _studio_service(db, request)
    try:
        detail = service.get_studio_detail(chart_id, current_user.id, question)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return detail.insight


@router.get("/{chart_id}/search")
def search_chart(
    chart_id: int,
    request: Request,
    q: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    service = _studio_service(db, request)
    try:
        return service.search_chart(chart_id, current_user.id, q)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
