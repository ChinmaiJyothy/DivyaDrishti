"""Birth profile repository."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from divyadrishti.models import BirthProfile


class BirthProfileRepository:
    """Database operations for birth profiles."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user(self, user_id: int) -> list[BirthProfile]:
        return (
            self.db.query(BirthProfile)
            .filter(BirthProfile.user_id == user_id, BirthProfile.deleted_at.is_(None))
            .all()
        )

    def get_by_id(self, profile_id: int, user_id: int) -> BirthProfile | None:
        return (
            self.db.query(BirthProfile)
            .filter(BirthProfile.id == profile_id, BirthProfile.user_id == user_id, BirthProfile.deleted_at.is_(None))
            .first()
        )

    def create(self, profile: BirthProfile) -> BirthProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: BirthProfile) -> BirthProfile:
        profile.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def soft_delete(self, profile: BirthProfile) -> BirthProfile:
        profile.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)
        return profile
