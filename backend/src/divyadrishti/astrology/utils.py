"""Utility helpers for Vedic chart calculations."""

from datetime import UTC, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

from divyadrishti.astrology.constants import (
    NAKSHATRA_LORDS,
    NAKSHATRAS,
    SIGN_NAMES,
    SIGN_QUALITIES,
)
from divyadrishti.astrology.models import ChartData
from divyadrishti.reasoning.astrological.models import AstrologicalChart


def normalize_longitude(lon: float) -> float:
    """Normalize a longitude to [0, 360)."""
    while lon < 0:
        lon += 360.0
    while lon >= 360.0:
        lon -= 360.0
    return lon


def zodiac_sign_index(lon: float) -> int:
    """Return the 0-based zodiac sign index for a longitude."""
    return int(normalize_longitude(lon) // 30)


def zodiac_sign(lon: float) -> str:
    """Return the zodiac sign name for a longitude."""
    return SIGN_NAMES[zodiac_sign_index(lon)]


def sign_degree(lon: float) -> float:
    """Return the degree within the current sign (0-30)."""
    return normalize_longitude(lon) % 30.0


def get_nakshatra(lon: float) -> str:
    """Return the nakshatra name for a longitude."""
    index = int(normalize_longitude(lon) / (13.0 + 1.0 / 3.0))
    return NAKSHATRAS[min(index, 26)]


def get_nakshatra_index(lon: float) -> int:
    """Return the 0-based nakshatra index for a longitude."""
    return int(normalize_longitude(lon) / (13.0 + 1.0 / 3.0))


def get_nakshatra_pada(lon: float) -> int:
    """Return the nakshatra pada (1-4) for a longitude."""
    pos = normalize_longitude(lon) % (13.0 + 1.0 / 3.0)
    return int(pos / ((13.0 + 1.0 / 3.0) / 4.0)) + 1


def get_nakshatra_lord(lon: float) -> str:
    """Return the Vimshottari lord of the nakshatra for a longitude."""
    return NAKSHATRA_LORDS[get_nakshatra_index(lon)]


def get_house(planet_lon: float, lagna_lon: float) -> int:
    """Return the 1-based whole-sign house for a planet."""
    planet_sign = zodiac_sign_index(planet_lon)
    lagna_sign = zodiac_sign_index(lagna_lon)
    return ((planet_sign - lagna_sign) % 12) + 1


def get_sign_quality(lon: float) -> str:
    """Return the quality (movable/fixed/dual) of the sign for a longitude."""
    return SIGN_QUALITIES[zodiac_sign(lon)]


def get_navamsa_sign(lon: float) -> str:
    """Return the navamsa (D9) sign for a longitude.

    Movable signs start from Aries, fixed from Leo, dual from Sagittarius.
    """
    deg = sign_degree(lon)
    division = int(deg / (10.0 / 3.0))  # 3 degrees 20 minutes
    quality = SIGN_QUALITIES[zodiac_sign(lon)]
    if quality == "movable":
        start = 0
    elif quality == "fixed":
        start = 4
    else:  # dual
        start = 8
    return SIGN_NAMES[(start + division) % 12]


def get_navamsa(lon: float) -> tuple[str, float]:
    """Return the navamsa sign and degree in that sign for a longitude."""
    deg = sign_degree(lon)
    division = int(deg / (10.0 / 3.0))
    quality = SIGN_QUALITIES[zodiac_sign(lon)]
    if quality == "movable":
        start = 0
    elif quality == "fixed":
        start = 4
    else:
        start = 8
    navamsa_sign_idx = (start + division) % 12
    navamsa_degree = (deg % (10.0 / 3.0)) * 9.0  # scale up to 30 degrees
    return SIGN_NAMES[navamsa_sign_idx], navamsa_degree


def get_varga_sign(lon: float, chart_type: str) -> str:
    """Return the varga sign for common divisional charts.

    Currently supports rashi (D1) and navamsa (D9). Dasamsa (D10),
    saptamsa (D7), and shashtiamsa (D60) are architecturally extendable.
    """
    if chart_type == "navamsa":
        return get_navamsa_sign(lon)
    return zodiac_sign(lon)


def parse_birth_datetime(
    date_of_birth: str,
    time_of_birth: str | None,
    timezone_name: str,
) -> datetime:
    """Parse local birth date/time and return UTC datetime.

    date_of_birth format: YYYY-MM-DD
    time_of_birth format: HH:MM or HH:MM:SS (defaults to 12:00)
    timezone_name: IANA zone or UTC offset string (+HH:MM / -HH:MM)
    """
    year, month, day = map(int, date_of_birth.split("-"))
    if time_of_birth and time_of_birth.strip():
        parts = time_of_birth.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
    else:
        hour, minute, second = 12, 0, 0

    tz = _parse_timezone(timezone_name)
    local_dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    return local_dt.astimezone(UTC)


def _parse_timezone(timezone_name: str) -> tzinfo:
    """Return a tzinfo object from an IANA name or a +/-HH:MM offset."""
    tz = timezone_name.strip()
    if tz.startswith(("+", "-")):
        sign = 1 if tz[0] == "+" else -1
        hours, minutes = tz[1:].split(":")
        offset = timedelta(hours=sign * int(hours), minutes=sign * int(minutes))
        return timezone(offset)
    if tz.upper() == "UTC" or tz == "":
        return UTC
    return ZoneInfo(tz)


def julian_day(utc_dt: datetime) -> float:
    """Return the Julian day for a UTC datetime."""
    import swisseph as swe

    return float(swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    ))


def _sign_distance(from_lon: float, to_lon: float) -> int:
    """Return the number of whole signs from one longitude to another."""
    return ((zodiac_sign_index(to_lon) - zodiac_sign_index(from_lon)) % 12) + 1


def _house_distance(from_lon: float, to_lon: float, lagna_lon: float) -> int:
    """Return the number of houses from from_lon to to_lon relative to lagna."""
    from_house = get_house(from_lon, lagna_lon)
    to_house = get_house(to_lon, lagna_lon)
    return ((to_house - from_house) % 12) + 1


def dms(deg: float) -> str:
    """Return a degree-minute-second string."""
    total = int(deg * 3600)
    d = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{d}°{m:02d}'{s:02d}"


def to_astrological_chart(chart_data: ChartData) -> AstrologicalChart:
    """Convert a ChartData model to an AstrologicalChart for reasoning."""

    planets = {}
    navamsa = {}
    nakshatras = {}
    for name, pos in chart_data.planets.items():
        planets[name] = {
            "house": pos.house,
            "sign": pos.sign,
            "nakshatra": pos.nakshatra,
            "dignity": pos.dignity,
            "retrograde": pos.retrograde,
            "combust": pos.combust,
            "degree": pos.degree,
        }
        if pos.navamsa_sign:
            navamsa[name] = {
                "house": pos.navamsa_house,
                "sign": pos.navamsa_sign,
                "nakshatra": pos.nakshatra,
                "dignity": pos.dignity,
                "retrograde": pos.retrograde,
                "combust": pos.combust,
                "degree": pos.navamsa_degree,
            }
        nakshatras[name] = pos.nakshatra

    return AstrologicalChart(
        lagna=chart_data.lagna,
        moon_sign=chart_data.moon_sign,
        sun_sign=chart_data.sun_sign,
        maha_dasha=chart_data.maha_dasha,
        antar_dasha=chart_data.antar_dasha,
        planets=planets,
        navamsa=navamsa,
        nakshatras=nakshatras,
        yogas=[y.name for y in chart_data.yogas],
        doshas=[d.name for d in chart_data.doshas],
    )
