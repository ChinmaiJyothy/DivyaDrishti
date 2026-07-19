"""Vimshottari dasha calculation helpers."""

from datetime import UTC, datetime
from typing import Any

from divyadrishti.astrology.constants import DASHA_SEQUENCE, DASHA_TOTAL_YEARS, DASHA_YEARS
from divyadrishti.astrology.utils import get_nakshatra_lord


def _dasha_index(lord: str) -> int:
    return DASHA_SEQUENCE.index(lord)


def _elapsed_fraction_of_nakshatra(moon_longitude: float) -> float:
    """Return the fraction of the moon's nakshatra already passed."""
    nakshatra_span = 13.0 + 1.0 / 3.0
    position_in_nakshatra = moon_longitude % nakshatra_span
    return position_in_nakshatra / nakshatra_span


def _maha_dasha_remaining_at_birth(moon_longitude: float) -> tuple[str, float]:
    """Return the first maha dasha lord and remaining years at birth."""
    lord = get_nakshatra_lord(moon_longitude)
    elapsed = _elapsed_fraction_of_nakshatra(moon_longitude)
    remaining = DASHA_YEARS[lord] * (1.0 - elapsed)
    return lord, remaining


def _dasha_start_dates(
    first_lord: str,
    first_remaining_years: float,
    birth_jd: float,
    birth_date: datetime,
) -> list[tuple[str, float, float]]:
    """Return the sequence of maha dasha lords with start and end Julian days."""
    results = []
    start_jd = birth_jd
    # First dasha starts at birth.
    end_jd = start_jd + first_remaining_years * 365.25
    idx = _dasha_index(first_lord)
    results.append((first_lord, start_jd, end_jd))
    start_jd = end_jd
    idx = (idx + 1) % len(DASHA_SEQUENCE)
    while len(results) < 9 * 3:  # cover 3 full cycles
        lord = DASHA_SEQUENCE[idx]
        end_jd = start_jd + DASHA_YEARS[lord] * 365.25
        results.append((lord, start_jd, end_jd))
        start_jd = end_jd
        idx = (idx + 1) % len(DASHA_SEQUENCE)
    return results


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian day to UTC datetime."""
    import swisseph as swe

    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return datetime(y, m, d, hour, minute, second)


def _format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def calculate_maha_dashas(
    moon_longitude: float,
    birth_jd: float,
    birth_date: datetime,
) -> list[dict[str, Any]]:
    """Return a list of maha dasha periods with start/end dates."""
    first_lord, first_remaining = _maha_dasha_remaining_at_birth(moon_longitude)
    periods = _dasha_start_dates(first_lord, first_remaining, birth_jd, birth_date)
    return [
        {
            "planet": lord,
            "start_date": _format_date(_jd_to_datetime(start_jd)),
            "end_date": _format_date(_jd_to_datetime(end_jd)),
            "is_current": False,
        }
        for lord, start_jd, end_jd in periods
    ]


def calculate_current_dasha(
    moon_longitude: float,
    birth_jd: float,
    birth_date: datetime,
    reference_date: datetime | None = None,
) -> tuple[str, str]:
    """Return the current maha and antar dasha lords for a reference date."""
    import swisseph as swe

    if reference_date is None:
        reference_date = datetime.now(UTC)
    if reference_date.tzinfo is not None:
        reference_date = reference_date.astimezone(UTC)
    reference_jd = swe.julday(
        reference_date.year,
        reference_date.month,
        reference_date.day,
        reference_date.hour + reference_date.minute / 60 + reference_date.second / 3600,
    )
    first_lord, first_remaining = _maha_dasha_remaining_at_birth(moon_longitude)
    periods = _dasha_start_dates(first_lord, first_remaining, birth_jd, birth_date)
    maha_lord = None
    maha_start = None
    maha_end = None
    for lord, start_jd, end_jd in periods:
        if start_jd <= reference_jd < end_jd:
            maha_lord = lord
            maha_start = start_jd
            maha_end = end_jd
            break
    if maha_lord is None or maha_start is None or maha_end is None:
        return first_lord, first_lord

    # Antar dasha within the maha dasha: proportional division of maha lord years.
    maha_span_years = (maha_end - maha_start) / 365.25

    start_idx = _dasha_index(maha_lord)
    antar_start = maha_start
    antar_lord = None
    for i in range(9):
        idx = (start_idx + i) % 9
        lord = DASHA_SEQUENCE[idx]
        years = DASHA_YEARS[lord]
        fraction = years / DASHA_TOTAL_YEARS
        segment = maha_span_years * fraction * 365.25
        if antar_start + segment > reference_jd:
            antar_lord = lord
            break
        antar_start += segment
    if antar_lord is None:
        antar_lord = maha_lord
    return maha_lord, antar_lord


def antar_dasha_periods_for_maha(
    maha_lord: str,
    maha_start_jd: float,
    maha_end_jd: float,
) -> list[dict]:
    """Return antar dasha periods within the current maha dasha."""
    maha_span = maha_end_jd - maha_start_jd
    start_idx = _dasha_index(maha_lord)
    periods = []
    current = maha_start_jd
    for i in range(9):
        idx = (start_idx + i) % 9
        lord = DASHA_SEQUENCE[idx]
        fraction = DASHA_YEARS[lord] / DASHA_TOTAL_YEARS
        end = current + maha_span * fraction
        periods.append(
            {
                "planet": lord,
                "start_date": _format_date(_jd_to_datetime(current)),
                "end_date": _format_date(_jd_to_datetime(end)),
                "is_current": False,
            }
        )
        current = end
    return periods
