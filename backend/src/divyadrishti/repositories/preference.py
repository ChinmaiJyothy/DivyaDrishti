"""User preference repository."""

from sqlalchemy.orm import Session

from divyadrishti.models import UserPreference


class PreferenceRepository:
    """Database operations for user preferences."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user(self, user_id: int) -> UserPreference | None:
        return self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def create(self, preference: UserPreference) -> UserPreference:
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference

    def update(self, preference: UserPreference) -> UserPreference:
        self.db.commit()
        self.db.refresh(preference)
        return preference
