"""Yoga detection for birth charts."""

from typing import Any


def _planet_sign(planets: dict[str, Any], name: str) -> str | None:
    pos = planets.get(name)
    return pos.sign if pos else None


def _planet_house(planets: dict[str, Any], name: str) -> int | None:
    pos = planets.get(name)
    return pos.house if pos else None


def _is_kendra(house: int) -> bool:
    return house in {1, 4, 7, 10}


def _is_trikona(house: int) -> bool:
    return house in {1, 5, 9}


def _house_distance(a: int, b: int) -> int:
    return ((b - a) % 12) or 12


def _signs_share(planet_a: str, planet_b: str, planets: dict[str, Any]) -> bool:
    return _planet_sign(planets, planet_a) == _planet_sign(planets, planet_b)


def _in_houses(planet: str, houses: set[int], planets: dict[str, Any]) -> bool:
    h = _planet_house(planets, planet)
    return h in houses if h is not None else False


def _dignity_strong(planet: str, planets: dict[str, Any]) -> bool:
    pos = planets.get(planet)
    if not pos:
        return False
    return pos.dignity in {"exalted", "moolatrikona", "own"}


def _lord_of_sign(sign: str, planets: dict[str, Any]) -> str | None:
    for name, pos in planets.items():
        if pos.lord == sign:
            return name
    return None


def detect_yogas(planets: dict[str, Any], lagna_lon: float) -> list[dict[str, Any]]:
    """Detect a subset of important Vedic yogas."""
    yogas = []
    moon_house = _planet_house(planets, "Moon")
    jupiter_house = _planet_house(planets, "Jupiter")
    sun_sign = _planet_sign(planets, "Sun")
    mercury_sign = _planet_sign(planets, "Mercury")
    mars_house = _planet_house(planets, "Mars")

    if moon_house and jupiter_house and _house_distance(moon_house, jupiter_house) in {1, 4, 7, 10}:
        yogas.append(
                {
                    "name": "Gaja Kesari Yoga",
                    "strength": "strong" if _dignity_strong("Jupiter", planets) else "moderate",
                    "description": "Jupiter in a kendra from Moon bestows wisdom, prosperity, and protection.",
                    "conditions": ["Jupiter in 1,4,7,10 from Moon"],
                    "matched_conditions": [f"Jupiter in house {jupiter_house}, Moon in house {moon_house}"],
                    "current_relevance": "Favorable for wisdom, stability, and public respect.",
                    "references": ["BPHS: Gaja Kesari Yoga"],
                }
            )

    if sun_sign and mercury_sign and sun_sign == mercury_sign:
        yogas.append(
            {
                "name": "Budha Aditya Yoga",
                "strength": "strong" if _dignity_strong("Mercury", planets) else "moderate",
                "description": "Sun and Mercury in the same sign produces intelligence, communication skills, and authority.",
                "conditions": ["Sun and Mercury in same sign"],
                "matched_conditions": [f"Sun and Mercury in {sun_sign}"],
                "current_relevance": "Favorable for intellect, education, and leadership.",
                "references": ["BPHS: Budha Aditya Yoga"],
            }
        )

    if moon_house and mars_house and _house_distance(moon_house, mars_house) in {1, 7}:
        yogas.append(
            {
                "name": "Chandra Mangala Yoga",
                "strength": "moderate",
                "description": "Moon and Mars conjoined or in opposition gives courage and enterprise.",
                "conditions": ["Moon and Mars in 1st or 7th from each other"],
                "matched_conditions": [f"Moon house {moon_house}, Mars house {mars_house}"],
                "current_relevance": "Can drive ambition, energy, and real-estate gains.",
                "references": ["BPHS: Chandra Mangala Yoga"],
            }
        )

    # Hamsa, Malavya, etc. (Pancha Mahapurusha)
    for planet, name, sign in [
        ("Jupiter", "Hamsa Yoga", "Sagittarius"),
        ("Jupiter", "Hamsa Yoga", "Pisces"),
        ("Venus", "Malavya Yoga", "Taurus"),
        ("Venus", "Malavya Yoga", "Libra"),
        ("Mars", "Ruchaka Yoga", "Aries"),
        ("Mars", "Ruchaka Yoga", "Scorpio"),
        ("Mercury", "Bhadra Yoga", "Gemini"),
        ("Mercury", "Bhadra Yoga", "Virgo"),
        ("Saturn", "Shasha Yoga", "Capricorn"),
        ("Saturn", "Shasha Yoga", "Aquarius"),
    ]:
        pos = planets.get(planet)
        if pos and pos.sign == sign and pos.house in {1, 4, 7, 10}:
            yogas.append(
                {
                    "name": name,
                    "strength": "strong",
                    "description": f"{planet} in own sign in a kendra forms {name}, granting excellence.",
                    "conditions": [f"{planet} in own sign in kendra"],
                    "matched_conditions": [f"{planet} in {sign} in house {pos.house}"],
                    "current_relevance": f"Strengthens the qualities of {planet}.",
                    "references": ["BPHS: Pancha Mahapurusha Yogas"],
                }
            )

    # Simple Raj Yoga: trine + kendra lord conjunction
    kendra_lords = {1: "Mars", 4: "Moon", 7: "Venus", 10: "Saturn"}
    trikona_lords = {1: "Mars", 5: "Sun", 9: "Jupiter"}
    kendra_planets = {kendra_lords[h]: h for h in kendra_lords if h == _planet_house(planets, kendra_lords[h])}
    trikona_planets = {trikona_lords[h]: h for h in trikona_lords if h == _planet_house(planets, trikona_lords[h])}
    for k_planet, _ in kendra_planets.items():
        for t_planet, _ in trikona_planets.items():
            if _signs_share(k_planet, t_planet, planets):
                yogas.append(
                    {
                        "name": "Raja Yoga",
                        "strength": "strong",
                        "description": f"Kendra lord {k_planet} and trikona lord {t_planet} joined, producing success.",
                        "conditions": ["Kendra lord and trikona lord conjoined"],
                        "matched_conditions": [f"{k_planet} and {t_planet} in {_planet_sign(planets, k_planet)}"],
                        "current_relevance": "Auspicious for status, power, and recognition.",
                        "references": ["BPHS: Raja Yoga"],
                    }
                )

    # Dhana Yoga: 2nd and 11th lords joined
    second_lord = "Venus"  # natural; simplified for chart interpretation
    eleventh_lord = "Saturn"  # natural
    if _signs_share(second_lord, eleventh_lord, planets):
        yogas.append(
            {
                "name": "Dhana Yoga",
                "strength": "moderate",
                "description": "2nd and 11th lords joined indicate wealth and income.",
                "conditions": ["2nd and 11th lords conjoined"],
                "matched_conditions": [f"{second_lord} and {eleventh_lord} in {_planet_sign(planets, second_lord)}"],
                "current_relevance": "Favorable for financial growth and gains.",
                "references": ["BPHS: Dhana Yoga"],
            }
        )

    # Avoid duplicate names
    seen = set()
    unique = []
    for y in yogas:
        if y["name"] not in seen:
            seen.add(y["name"])
            unique.append(y)
    return unique
