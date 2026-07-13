"""JWT token utilities."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from divyadrishti.config import get_settings

settings = get_settings()


def create_access_token(subject: str) -> str:
    """Create a short-lived access token."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {"sub": subject, "exp": expires, "type": "access"}
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> tuple[str, str]:
    """Create a long-lived refresh token and return token + jti."""
    jti = str(uuid4())
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    data = {"sub": subject, "exp": expires, "type": "refresh", "jti": jti}
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm), jti


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
