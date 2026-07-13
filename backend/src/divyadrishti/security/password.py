"""Argon2 password hashing utilities."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against an Argon2 hash."""
    try:
        _hasher.verify(hashed, password)
    except VerifyMismatchError:
        return False
    return True
