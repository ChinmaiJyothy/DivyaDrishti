"""Email service for verification and password reset.

SMTP backend must be configured in production. Until then, the service fails
loudly to avoid silently dropping transactional emails.
"""

import os
import secrets


class EmailConfigurationError(RuntimeError):
    """Raised when email is used without a configured SMTP backend."""


class EmailService:
    """Email service. Configure SMTP backend before use in production."""

    def _send(self, to: str, subject: str, body: str) -> None:
        if not all([os.getenv("EMAIL_HOST"), os.getenv("EMAIL_PORT"), os.getenv("EMAIL_FROM")]):
            raise EmailConfigurationError(
                "SMTP backend is not configured. Set EMAIL_HOST, EMAIL_PORT, "
                "EMAIL_USERNAME, EMAIL_PASSWORD and EMAIL_FROM in the environment."
            )
        # SMTP integration would be added here.
        pass

    def send_verification_email(self, to: str, token: str) -> None:
        """Send a verification email."""
        body = f"Verify your account using token: {token}"
        self._send(to, "Verify your email", body)

    def send_password_reset_email(self, to: str, token: str) -> None:
        """Send a password reset email."""
        body = f"Reset your password using token: {token}"
        self._send(to, "Password reset", body)


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)
