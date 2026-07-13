"""User preference service."""

from sqlalchemy.orm import Session

from divyadrishti.models import UserPreference
from divyadrishti.repositories import PreferenceRepository


class PreferenceService:
    """Business logic for user preferences."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PreferenceRepository(db)

    def get(self, user_id: int) -> UserPreference:
        pref = self.repo.get_by_user(user_id)
        if not pref:
            pref = UserPreference(user_id=user_id)
            self.repo.create(pref)
        return pref

    def update(self, user_id: int, data: dict) -> UserPreference:
        pref = self.get(user_id)
        for key, value in data.items():
            if value is not None and hasattr(pref, key):
                setattr(pref, key, value)
        return self.repo.update(pref)
