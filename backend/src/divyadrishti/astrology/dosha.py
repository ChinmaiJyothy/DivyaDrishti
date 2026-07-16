"""Dosha detection for birth charts."""

from typing import Any


def _planet_house(planets: dict[str, Any], name: str) -> int | None:
    pos = planets.get(name)
    return pos.house if pos else None


def _planet_sign(planets: dict[str, Any], name: str) -> str | None:
    pos = planets.get(name)
    return pos.sign if pos else None


def detect_doshas(planets: dict[str, Any], lagna_lon: float) -> list[dict[str, Any]]:
    """Detect a subset of common Vedic doshas."""
    doshas = []

    mars_house = _planet_house(planets, "Mars")
    moon_house = _planet_house(planets, "Moon")
    saturn_house = _planet_house(planets, "Saturn")
    rahu_house = _planet_house(planets, "Rahu")
    ketu_house = _planet_house(planets, "Ketu")

    # Mangal Dosha
    if mars_house in {1, 2, 4, 7, 8, 12}:
        doshas.append(
            {
                "name": "Mangal Dosha",
                "severity": "high" if mars_house in {1, 7, 8} else "moderate",
                "conditions": ["Mars in 1, 2, 4, 7, 8, or 12 from Lagna"],
                "mitigating_factors": ["Jupiter aspect", "Mars in own/exaltation"],
                "confidence": 0.85,
                "references": ["BPHS: Mangal Dosha"],
            }
        )

    # Kaal Sarpa Dosha
    if rahu_house and ketu_house:
        all_houses = {_planet_house(planets, p) for p in planets if p not in {"Rahu", "Ketu"}}
        all_houses.discard(None)
        if all_houses and abs(rahu_house - ketu_house) == 6:
            half_min = min(rahu_house, ketu_house)
            half_max = max(rahu_house, ketu_house)
            if all(
                (half_min < h <= half_max or h > half_max or h <= half_min)
                for h in all_houses
                if h is not None
            ):
                doshas.append(
                    {
                        "name": "Kaal Sarp Dosha",
                        "severity": "moderate",
                        "conditions": ["All planets on one side of Rahu-Ketu axis"],
                        "mitigating_factors": ["Rahu/Ketu in kendra", "benefic aspects"],
                        "confidence": 0.6,
                        "references": ["BPHS: Kaal Sarpa"],
                    }
                )

    # Shani Sade Sati
    if moon_house:
        sade_sati_houses = {((moon_house - 2 - 1) % 12) + 1, moon_house, ((moon_house % 12) + 1)}
        if saturn_house in sade_sati_houses:
            doshas.append(
                {
                    "name": "Shani Sade Sati",
                    "severity": "high" if saturn_house == moon_house else "moderate",
                    "conditions": ["Saturn in 12th, 1st, or 2nd from Moon"],
                    "mitigating_factors": ["Saturn in own/exaltation", "Jupiter aspect"],
                    "confidence": 0.8,
                    "references": ["BPHS: Shani Sade Sati"],
                }
            )

    # Guru Chandal Dosha
    jupiter_house = _planet_house(planets, "Jupiter")
    if jupiter_house and rahu_house and jupiter_house == rahu_house:
        doshas.append(
            {
                "name": "Guru Chandal Dosha",
                "severity": "moderate",
                "conditions": ["Jupiter and Rahu conjoined"],
                "mitigating_factors": ["Jupiter strong", "other benefics in kendra"],
                "confidence": 0.75,
                "references": ["BPHS: Guru Chandal"],
            }
        )

    # Pitru Dosha (Sun with Rahu/Ketu/Saturn)
    sun_house = _planet_house(planets, "Sun")
    if sun_house and sun_house in (rahu_house, ketu_house, saturn_house):
        doshas.append(
            {
                "name": "Pitru Dosha",
                "severity": "moderate",
                "conditions": ["Sun conjoined with Rahu, Ketu, or Saturn"],
                "mitigating_factors": ["Sun strong in own/exaltation", "remedies"],
                "confidence": 0.65,
                "references": ["BPHS: Pitru Dosha"],
            }
        )

    return doshas
