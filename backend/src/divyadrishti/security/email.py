"""Email stub for verification and password reset."""

import secrets
from typing import Any


class EmailService:
    """Email service architecture. Actual SMTP backend not configured."""

    def send_verification_email(self, to: str, token: str) -> None:
        """Queue a verification email."""
        # SMTP integration would be added here.
        pass

    def send_password_reset_email(self, to: str, token: str) -> None:
        """Queue a password reset email."""
        pass


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)
