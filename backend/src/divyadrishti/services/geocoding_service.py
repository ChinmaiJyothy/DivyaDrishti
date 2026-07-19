"""Geocoding and timezone resolution for birth profiles."""

from dataclasses import dataclass

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


@dataclass
class GeoResult:
    latitude: float
    longitude: float
    timezone: str
    display_name: str | None = None


class GeocodingService:
    """Resolve a place name to latitude, longitude and IANA timezone."""

    def __init__(self, user_agent: str = "divyadrishti/0.1.0") -> None:
        self.geolocator = Nominatim(user_agent=user_agent, timeout=10)
        self.tz_finder = TimezoneFinder()

    def resolve(
        self,
        place: str | None,
        latitude: float | None = None,
        longitude: float | None = None,
        timezone: str | None = None,
    ) -> GeoResult:
        """Return resolved coordinates and timezone.

        If latitude/longitude/timezone are all provided, they are used
        as-is.  Otherwise the place name is geocoded and the timezone is
        derived from the coordinates.
        """
        if latitude is not None and longitude is not None and timezone:
            return GeoResult(
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                display_name=place,
            )

        if not place:
            raise ValueError("A birth place is required when latitude/longitude/timezone are not provided.")

        try:
            location = self.geolocator.geocode(place, exactly_one=True, language="en")
        except (GeocoderTimedOut, GeocoderServiceError) as exc:
            raise RuntimeError(f"Geocoding service unavailable for '{place}': {exc}") from exc

        if not location:
            raise ValueError(f"Could not geocode birth place: {place}")

        lat = location.latitude
        lon = location.longitude

        tz = timezone or self.tz_finder.timezone_at(lng=lon, lat=lat)
        if not tz:
            tz = "UTC"

        return GeoResult(
            latitude=lat,
            longitude=lon,
            timezone=tz,
            display_name=location.address,
        )
