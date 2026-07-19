"""Deterministic unit tests for Vimshottari Dasha calculations."""

from datetime import UTC, datetime

import pytest
import swisseph as swe

from divyadrishti.astrology.constants import DASHA_SEQUENCE, DASHA_YEARS
from divyadrishti.astrology.dasha import (
    _dasha_index,
    _elapsed_fraction_of_nakshatra,
    _maha_dasha_remaining_at_birth,
    calculate_current_dasha,
    calculate_maha_dashas,
)
from divyadrishti.astrology.utils import get_nakshatra_lord, julian_day, parse_birth_datetime


# Reference data for the Chinmai profile used in the generator tests.
CHINMAI_DOB = "2001-11-27"
CHINMAI_TOB = "10:45"
CHINMAI_TZ = "Asia/Kolkata"


@pytest.fixture
def chinmai_moon_longitude() -> float:
    """Return the sidereal Lahiri Moon longitude for the Chinmai profile."""
    utc_dt = parse_birth_datetime(CHINMAI_DOB, CHINMAI_TOB, CHINMAI_TZ)
    jd = julian_day(utc_dt)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_MOSEPH)
    return float(res[0])


@pytest.fixture
def chinmai_birth_jd() -> float:
    utc_dt = parse_birth_datetime(CHINMAI_DOB, CHINMAI_TOB, CHINMAI_TZ)
    return julian_day(utc_dt)


@pytest.fixture
def chinmai_birth_date() -> datetime:
    return parse_birth_datetime(CHINMAI_DOB, CHINMAI_TOB, CHINMAI_TZ)


def test_maha_dasha_sequence_starts_with_nakshatra_lord(
    chinmai_moon_longitude: float,
    chinmai_birth_jd: float,
    chinmai_birth_date: datetime,
) -> None:
    """The first maha dasha must be the lord of the Moon's nakshatra."""
    dashas = calculate_maha_dashas(chinmai_moon_longitude, chinmai_birth_jd, chinmai_birth_date)
    expected_lord = get_nakshatra_lord(chinmai_moon_longitude)
    assert dashas[0]["planet"] == expected_lord
    assert dashas[0]["planet"] == "Mercury"  # Moon is in Revati in this reference chart


def test_first_dasha_remaining_years_use_elapsed_fraction(
    chinmai_moon_longitude: float,
) -> None:
    """The balance of the first dasha is proportional to the Moon's nakshatra progress."""
    lord, remaining = _maha_dasha_remaining_at_birth(chinmai_moon_longitude)
    elapsed = _elapsed_fraction_of_nakshatra(chinmai_moon_longitude)
    assert remaining == pytest.approx(DASHA_YEARS[lord] * (1 - elapsed), abs=1e-9)
    # For Revati the Moon is near the end, so the remaining Mercury years are small.
    assert remaining < DASHA_YEARS[lord]


def test_dasha_sequence_follows_vimshottari_order() -> None:
    """After the first lord, dashas follow the fixed Vimshottari sequence."""
    moon_lon = 0.0  # Ashwini, lord Ketu
    jd = 2_451_545.0  # arbitrary JD
    birth_date = datetime(2000, 1, 1, 12, 0, tzinfo=UTC)
    dashas = calculate_maha_dashas(moon_lon, jd, birth_date)
    start_index = _dasha_index("Ketu")
    for i, dasha in enumerate(dashas[:9]):
        expected = DASHA_SEQUENCE[(start_index + i) % 9]
        assert dasha["planet"] == expected


def test_current_dasha_for_chinmai_reference_date(
    chinmai_moon_longitude: float,
    chinmai_birth_jd: float,
    chinmai_birth_date: datetime,
) -> None:
    """For 2026-07-19 UTC the reference profile should be in Venus/Saturn antar."""
    reference = datetime(2026, 7, 19, 0, 0, 0, tzinfo=UTC)
    maha, antar = calculate_current_dasha(
        chinmai_moon_longitude,
        chinmai_birth_jd,
        chinmai_birth_date,
        reference_date=reference,
    )
    assert maha == "Venus"
    assert antar == "Saturn"


def test_current_dasha_at_birth_is_first_lord(
    chinmai_moon_longitude: float,
    chinmai_birth_jd: float,
    chinmai_birth_date: datetime,
) -> None:
    """At the moment of birth the current maha and antar dasha are the first lord."""
    maha, antar = calculate_current_dasha(
        chinmai_moon_longitude,
        chinmai_birth_jd,
        chinmai_birth_date,
        reference_date=chinmai_birth_date,
    )
    expected = get_nakshatra_lord(chinmai_moon_longitude)
    assert maha == expected
    assert antar == expected
