"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.schemas.auth import (
    EmailVerifyRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from divyadrishti.services.authentication_service import AuthenticationService

router = APIRouter(prefix="/auth", tags=["auth"])


def _handle_service_error(exc: Exception) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserRegisterRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    try:
        user = service.register(body.email, body.password, body.name)
    except ValueError as exc:
        _handle_service_error(exc)

    tokens = service.login(body.email, body.password)
    return tokens


@router.post("/login", response_model=TokenResponse)
def login(body: UserLoginRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    try:
        return service.login(body.email, body.password)
    except ValueError as exc:
        _handle_service_error(exc)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    try:
        return service.refresh(body.refresh_token)
    except ValueError as exc:
        _handle_service_error(exc)


@router.post("/logout")
def logout(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    service.logout(body.refresh_token)
    return {"detail": "Logged out successfully"}


@router.post("/verify-email")
def verify_email(body: EmailVerifyRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    try:
        service.verify_email(body.token)
    except ValueError as exc:
        _handle_service_error(exc)
    return {"detail": "Email verified"}


@router.post("/request-password-reset")
def request_password_reset(body: PasswordResetRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    service.request_password_reset(body.email)
    return {"detail": "Password reset requested"}


@router.post("/reset-password")
def reset_password(body: PasswordResetConfirmRequest, db: Session = Depends(get_db)):
    service = AuthenticationService(db)
    try:
        service.reset_password(body.token, body.new_password)
    except ValueError as exc:
        _handle_service_error(exc)
    return {"detail": "Password reset successfully"}
