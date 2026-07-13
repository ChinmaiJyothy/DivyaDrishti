"""Birth profile API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.birth_profile import (
    BirthProfileCreateRequest,
    BirthProfileResponse,
    BirthProfileUpdateRequest,
)
from divyadrishti.security import get_current_user
from divyadrishti.services.birth_profile_service import BirthProfileService

router = APIRouter(prefix="/profiles", tags=["birth profiles"])


def _service(db: Session) -> BirthProfileService:
    return BirthProfileService(db)


@router.post("", response_model=BirthProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    body: BirthProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _service(db).create(current_user.id, body.model_dump())


@router.get("", response_model=list[BirthProfileResponse])
def list_profiles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _service(db).list(current_user.id)


@router.get("/{profile_id}", response_model=BirthProfileResponse)
def get_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _service(db).get(profile_id, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=BirthProfileResponse)
def update_profile(
    profile_id: int,
    body: BirthProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    profile = service.get(profile_id, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return service.update(profile, body.model_dump(exclude_unset=True))


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    profile = service.get(profile_id, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    service.delete(profile)
    return {"detail": "Profile deleted"}
