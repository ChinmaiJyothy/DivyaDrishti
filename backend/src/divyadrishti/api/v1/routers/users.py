"""User API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.user import UserResponse, UserUpdateRequest
from divyadrishti.security import get_current_user
from divyadrishti.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService(db).get_me(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).update_me(current_user, body.model_dump(exclude_unset=True))


@router.delete("/me")
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    UserService(db).delete_me(current_user)
    return {"detail": "Account deleted"}
