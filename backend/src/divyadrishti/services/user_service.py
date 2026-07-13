"""User service."""

from sqlalchemy.orm import Session

from divyadrishti.models import User
from divyadrishti.repositories import UserRepository
from divyadrishti.services.preference_service import PreferenceService


class UserService:
    """Business logic for user profiles."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)
        self.preference_service = PreferenceService(db)

    def get_me(self, user: User) -> User:
        return user

    def update_me(self, user: User, data: dict) -> User:
        user_fields = {"name", "email"}
        pref_fields = {
            "preferred_language",
            "preferred_explanation_depth",
            "preferred_astrology_school",
            "preferred_chart_style",
            "citation_mode",
            "dark_mode",
            "units",
            "notification_settings",
            "timezone",
            "country",
            "theme_preference",
            "privacy_settings",
        }

        for key, value in data.items():
            if value is None:
                continue
            if key in user_fields and hasattr(user, key):
                setattr(user, key, value)
            elif key in pref_fields:
                self.preference_service.update(user.id, {key: value})

        self.repo.update(user)
        return user

    def delete_me(self, user: User) -> User:
        return self.repo.soft_delete(user)
