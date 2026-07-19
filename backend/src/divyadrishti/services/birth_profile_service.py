"""Birth profile service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from divyadrishti.models import BirthProfile
from divyadrishti.repositories import BirthProfileRepository
from divyadrishti.services.geocoding_service import GeocodingService


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
        if self._should_resolve(profile=None, data=data):
            resolved = self._resolve_location(data)
            data["latitude"] = resolved["latitude"]
            data["longitude"] = resolved["longitude"]
            data["timezone"] = resolved["timezone"]
        # Fall back to UTC when no location/timezone information is supplied.
        if not data.get("timezone"):
            data["timezone"] = "UTC"
        profile = BirthProfile(user_id=user_id, **data)
        return self.repo.create(profile)

    def update(self, profile: BirthProfile, data: dict) -> BirthProfile:
        if self._should_resolve(profile=profile, data=data):
            merged = {
                "birth_place": data.get("birth_place") or profile.birth_place,
                "latitude": data.get("latitude") if "latitude" in data else profile.latitude,
                "longitude": data.get("longitude") if "longitude" in data else profile.longitude,
                "timezone": data.get("timezone") if "timezone" in data else profile.timezone,
            }
            resolved = self._resolve_location(merged)
            data["latitude"] = resolved["latitude"]
            data["longitude"] = resolved["longitude"]
            data["timezone"] = resolved["timezone"]

        for key, value in data.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        return self.repo.update(profile)

    def delete(self, profile: BirthProfile) -> BirthProfile:
        return self.repo.soft_delete(profile)

    @staticmethod
    def _resolve_location(data: dict) -> dict:
        geocoder = GeocodingService()
        result = geocoder.resolve(
            place=data.get("birth_place"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            timezone=data.get("timezone"),
        )
        return {
            "latitude": result.latitude,
            "longitude": result.longitude,
            "timezone": result.timezone,
        }

    @staticmethod
    def _should_resolve(profile: BirthProfile | None, data: dict) -> bool:
        """Resolve coordinates when a place is supplied or coords need filling."""
        birth_place = data.get("birth_place") or (profile.birth_place if profile else None)
        if not birth_place:
            return False
        lat = data.get("latitude") or (profile.latitude if profile else None)
        lon = data.get("longitude") or (profile.longitude if profile else None)
        tz = data.get("timezone") or (profile.timezone if profile else None)
        # Re-resolve if birth_place changed or any coordinate/timezone is missing.
        return "birth_place" in data or lat is None or lon is None or not tz
