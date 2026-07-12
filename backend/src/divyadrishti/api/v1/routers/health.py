from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from divyadrishti.infrastructure.persistence.database import get_db
from divyadrishti.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/health/db", response_model=HealthResponse)
def db_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", version="0.1.0")
