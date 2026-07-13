"""Authentication service."""

from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy.orm import Session

from divyadrishti.models import RefreshToken, Role, User, UserPreference
from divyadrishti.repositories import UserRepository
from divyadrishti.security.email import EmailService, generate_token
from divyadrishti.security.password import hash_password, verify_password
from divyadrishti.security.token import create_access_token, create_refresh_token, decode_token


def _expiry_from_token(token: str) -> datetime:
    payload = decode_token(token)
    exp = payload["exp"]
    return datetime.fromtimestamp(exp, tz=timezone.utc)


class AuthenticationService:
    """Handle registration, login, token refresh, and logout."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)
        self.email = EmailService()

    def register(self, email: str, password: str, name: str, role_name: str = "user") -> User:
        if self.repo.get_by_email(email):
            raise ValueError("User already exists")

        role = self.repo.get_role_by_name(role_name)
        if not role:
            role = self._ensure_role(role_name)

        user = User(
            email=email,
            name=name,
            hashed_password=hash_password(password),
            role_id=role.id,
            verification_token=generate_token(),
        )
        self.repo.create(user)
        # Create default preferences
        self.db.add(UserPreference(user_id=user.id))
        self.db.commit()
        self.email.send_verification_email(user.email, user.verification_token)
        return user

    def login(self, email: str, password: str) -> dict:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(str(user.id))
        refresh_token, jti = create_refresh_token(str(user.id))
        token_hash = sha256(refresh_token.encode()).hexdigest()

        self.repo.create_refresh_token(
            RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=_expiry_from_token(refresh_token),
            )
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        token_hash = sha256(refresh_token.encode()).hexdigest()
        stored = self.repo.get_refresh_token(token_hash)
        if not stored or stored.revoked_at or stored.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token revoked or expired")

        user_id = int(payload["sub"])
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Revoke old token
        stored.revoked_at = datetime.now(timezone.utc)
        self.db.commit()

        access_token = create_access_token(str(user.id))
        new_refresh_token, _ = create_refresh_token(str(user.id))
        new_hash = sha256(new_refresh_token.encode()).hexdigest()
        self.repo.create_refresh_token(
            RefreshToken(
                user_id=user.id,
                token_hash=new_hash,
                expires_at=_expiry_from_token(new_refresh_token),
            )
        )
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    def logout(self, refresh_token: str) -> None:
        token_hash = sha256(refresh_token.encode()).hexdigest()
        stored = self.repo.get_refresh_token(token_hash)
        if stored and not stored.revoked_at:
            stored.revoked_at = datetime.now(timezone.utc)
            self.db.commit()

    def verify_email(self, token: str) -> User:
        user = self.db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise ValueError("Invalid verification token")
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        return user

    def request_password_reset(self, email: str) -> None:
        user = self.repo.get_by_email(email)
        if user:
            user.reset_token = generate_token()
            self.db.commit()
            self.email.send_password_reset_email(user.email, user.reset_token)

    def reset_password(self, token: str, new_password: str) -> User:
        user = self.db.query(User).filter(User.reset_token == token).first()
        if not user:
            raise ValueError("Invalid reset token")
        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        self.db.commit()
        return user

    def _ensure_role(self, name: str) -> Role:
        role = self.repo.get_role_by_name(name)
        if not role:
            role = Role(name=name)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        return role
