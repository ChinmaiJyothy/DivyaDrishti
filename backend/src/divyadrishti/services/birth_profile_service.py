"""Birth profile service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from divyadrishti.models import BirthProfile
from divyadrishti.repositories import BirthProfileRepository


class BirthProfileService:
    """Business logic for birth profiles."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BirthProfileRepository(db)

    def list(self, user_id: int) -> list[BirthProfile]:
        return self.repo.list_by_user(user_id)

    def get(self, profile_id: int, user_id: int) -> BirthProfile | None:
        return self.repo.get_by_id(profile_id, user_id)

    def create(self, user_id: int, data: dict) -> BirthProfile:
        profile = BirthProfile(user_id=user_id, **data)
        return self.repo.create(profile)

    def update(self, profile: BirthProfile, data: dict) -> BirthProfile:
        for key, value in data.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        return self.repo.update(profile)

    def delete(self, profile: BirthProfile) -> BirthProfile:
        return self.repo.soft_delete(profile)
