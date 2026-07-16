"""Planetary aspect calculation."""

from typing import Any

from divyadrishti.astrology.constants import ASPECT_HOUSES
from divyadrishti.astrology.models import AspectDetail


def _house_distance(from_house: int, to_house: int) -> int:
    return ((to_house - from_house) % 12) or 12


def calculate_aspects(
    planets: dict[str, Any], lagna_lon: float
) -> tuple[list[AspectDetail], dict[str, list[str]]]:
    """Return Vedic aspect relationships and a mapping of planet -> aspected planets."""
    aspects: list[AspectDetail] = []
    planet_aspects: dict[str, list[str]] = {name: [] for name in planets}

    for source_name, source_pos in planets.items():
        for target_name, target_pos in planets.items():
            if source_name == target_name:
                continue
            distance = _house_distance(source_pos.house, target_pos.house)
            if distance in ASPECT_HOUSES.get(source_name, {7}):
                orb = abs(source_pos.longitude - target_pos.longitude)
                if orb > 180:
                    orb = 360 - orb
                planet_aspects[source_name].append(target_name)
                aspects.append(
                    AspectDetail(
                        source=source_name,
                        target=target_name,
                        aspect_houses=[distance],
                        orb=round(orb, 2),
                        type="special" if distance != 7 else "full",
                    )
                )

    return aspects, planet_aspects
