"""User preference API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.preference import PreferenceResponse, PreferenceUpdateRequest
from divyadrishti.security import get_current_user
from divyadrishti.services.preference_service import PreferenceService

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return PreferenceService(db).get(current_user.id)


@router.patch("", response_model=PreferenceResponse)
def update_preferences(
    body: PreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PreferenceService(db).update(current_user.id, body.model_dump(exclude_unset=True))
