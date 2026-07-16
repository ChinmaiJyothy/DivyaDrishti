"""Birth chart generation using pyswisseph."""

from datetime import datetime
from typing import Any

import swisseph as swe

from divyadrishti.astrology.constants import (
    ASPECT_HOUSES,
    COMBUST_ORBS,
    DIGNITY_FRIENDLY,
    PLANET_DEBILITATION,
    PLANET_ENEMY_SIGNS,
    PLANET_EXALTATION,
    PLANET_FRIEND_SIGNS,
    PLANET_MOOLATRIKONA,
    PLANET_OWN_SIGNS,
    PLANET_SWISS_IDS,
    SIGN_LORDS,
    SIGN_NAMES,
    VALID_PLANETS,
)
from divyadrishti.astrology.dasha import calculate_current_dasha, calculate_maha_dashas
from divyadrishti.astrology.dosha import detect_doshas
from divyadrishti.astrology.models import (
    AspectDetail,
    ChartData,
    DashaPeriod,
    DoshaDetail,
    HousePosition,
    NakshatraDetail,
    PlanetPosition,
    TransitPosition,
    VargaChart,
    YogaDetail,
)
from divyadrishti.astrology.utils import (
    get_house,
    get_nakshatra,
    get_nakshatra_lord,
    get_nakshatra_pada,
    get_navamsa,
    get_varga_sign,
    julian_day,
    parse_birth_datetime,
    sign_degree,
    zodiac_sign,
    zodiac_sign_index,
)
from divyadrishti.astrology.yoga import detect_yogas

# Default Swiss Ephemeris flags: sidereal Lahiri ayanamsha, Moshier fallback.
# pyswisseph 2.10.x exposes these as FLG_* constants.
DEFAULT_FLAGS = swe.FLG_SIDEREAL | swe.FLG_MOSEPH


def _set_sidereal() -> None:
    """Configure Swiss Ephemeris for sidereal Lahiri calculations."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    swe.set_ephe_path(None)


def _compute_dignity(planet: str, sign: str, longitude: float) -> str:
    """Return the dignity of a planet in a sign."""
    if PLANET_EXALTATION.get(planet) == sign:
        return "exalted"
    if PLANET_DEBILITATION.get(planet) == sign:
        return "debilitated"

    mool_min, mool_max = PLANET_MOOLATRIKONA.get(planet, (None, None))
    if mool_min and sign in {mool_min, mool_max}:
        return "moolatrikona"

    if sign in PLANET_OWN_SIGNS.get(planet, set()):
        return "own"

    if sign in PLANET_FRIEND_SIGNS.get(planet, set()):
        return "friendly"
    if sign in PLANET_ENEMY_SIGNS.get(planet, set()):
        return "enemy"
    if sign in DIGNITY_FRIENDLY.get(planet, set()):
        return "friendly"

    return "neutral"


def _is_combust(planet: str, planet_lon: float, sun_lon: float) -> bool:
    """Return True if the planet is within combustion orb of the Sun."""
    orb = COMBUST_ORBS.get(planet, 0.0)
    if orb == 0.0:
        return False
    diff = abs(planet_lon - sun_lon)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb


class BirthChartGenerator:
    """Generate Vedic birth charts using the Swiss Ephemeris."""

    def __init__(self) -> None:
        _set_sidereal()

    def _compute_planet(
        self,
        name: str,
        longitude: float,
        sun_lon: float,
        lagna_lon: float,
        chart_type: str = "rashi",
        jd: float = 0.0,
    ) -> PlanetPosition:
        if chart_type == "navamsa":
            sign, sign_degree_value = get_navamsa(longitude)
            # Navamsa houses are relative to navamsa lagna.
            navamsa_lagna = get_varga_sign(lagna_lon, "navamsa")
            navamsa_lagna_idx = SIGN_NAMES.index(navamsa_lagna)
            sign_idx = SIGN_NAMES.index(sign)
            house = ((sign_idx - navamsa_lagna_idx) % 12) + 1
            navamsa_sign = sign
            navamsa_house = house
        else:
            sign = zodiac_sign(longitude)
            sign_degree_value = sign_degree(longitude)
            house = get_house(longitude, lagna_lon)
            navamsa_sign, navamsa_degree_value = get_navamsa(longitude)
            navamsa_lagna = get_varga_sign(lagna_lon, "navamsa")
            navamsa_lagna_idx = SIGN_NAMES.index(navamsa_lagna)
            navamsa_sign_idx = SIGN_NAMES.index(navamsa_sign)
            navamsa_house = ((navamsa_sign_idx - navamsa_lagna_idx) % 12) + 1

        dignity = _compute_dignity(name, sign, longitude)
        retrograde = self._is_retrograde(name, jd) if jd else False
        combust = _is_combust(name, longitude, sun_lon) if chart_type == "rashi" else False

        return PlanetPosition(
            name=name,
            longitude=round(longitude, 6),
            sign=sign,
            sign_degree=round(sign_degree_value, 4),
            house=house,
            nakshatra=get_nakshatra(longitude),
            nakshatra_pada=get_nakshatra_pada(longitude),
            nakshatra_lord=get_nakshatra_lord(longitude),
            dignity=dignity,
            retrograde=retrograde,
            combust=combust,
            degree=round(sign_degree_value, 4),
            lord=SIGN_LORDS.get(sign),
            navamsa_sign=navamsa_sign,
            navamsa_house=navamsa_house,
            navamsa_degree=round(navamsa_degree_value, 4) if chart_type != "navamsa" else round(sign_degree_value, 4),
        )

    def _is_retrograde(self, name: str, jd: float) -> bool:
        """Return True if the planet appears retrograde at this longitude."""
        if name == "Ketu":
            return True
        if name == "Rahu":
            # Mean node is always retrograde in Vedic practice.
            return True
        swiss_id = PLANET_SWISS_IDS.get(name)
        if swiss_id is None or swiss_id < 0:
            return False
        res, _ = swe.calc_ut(jd, swiss_id, DEFAULT_FLAGS | swe.FLG_SPEED)
        return bool(res[3] < 0.0)

    def _compute_planets(
        self,
        jd: float,
        lagna_lon: float,
        chart_type: str = "rashi",
    ) -> dict[str, PlanetPosition]:
        """Compute all planet positions for the chart."""
        sun_res, _ = swe.calc_ut(jd, PLANET_SWISS_IDS["Sun"], DEFAULT_FLAGS)
        sun_lon = sun_res[0]

        planets: dict[str, PlanetPosition] = {}
        for name in VALID_PLANETS:
            if name == "Ketu":
                # Ketu is 180° from Rahu.
                rahu_pos = planets.get("Rahu")
                if not rahu_pos:
                    continue
                lon = (rahu_pos.longitude + 180.0) % 360.0
                pos = self._compute_planet(name, lon, sun_lon, lagna_lon, chart_type)
                pos.retrograde = True
                planets[name] = pos
                continue

            swiss_id = PLANET_SWISS_IDS[name]
            res, _ = swe.calc_ut(jd, swiss_id, DEFAULT_FLAGS)
            lon = res[0]
            retrograde = self._is_retrograde(name, jd)
            pos = self._compute_planet(name, lon, sun_lon, lagna_lon, chart_type, jd)
            pos.retrograde = retrograde
            planets[name] = pos

        return planets

    def _compute_lagna(self, jd: float, lat: float, lon: float) -> float:
        """Compute the ascendant (Lagna) longitude."""
        _, ascmc = swe.houses_ex(jd, lat, lon, b"W", DEFAULT_FLAGS)
        return float(ascmc[0])

    def generate(
        self,
        date_of_birth: str,
        time_of_birth: str | None,
        latitude: float,
        longitude: float,
        timezone: str,
        chart_type: str = "rashi",
    ) -> ChartData:
        """Generate a complete chart for the given birth data."""
        utc_dt = parse_birth_datetime(date_of_birth, time_of_birth, timezone)
        jd = julian_day(utc_dt)
        lat = latitude
        lon = longitude

        lagna_lon = self._compute_lagna(jd, lat, lon)
        planets = self._compute_planets(jd, lagna_lon, chart_type)

        # Houses for D1; for varga, houses are recomputed from the varga lagna.
        houses = self._compute_houses(planets, lagna_lon, chart_type)

        # Nakshatra details.
        nakshatras = self._compute_nakshatra_details(planets)

        # Dashas.
        moon_pos = planets.get("Moon")
        if moon_pos:
            dashas = calculate_maha_dashas(moon_pos.longitude, jd, utc_dt)
            maha_dasha, antar_dasha = calculate_current_dasha(moon_pos.longitude, jd, utc_dt)
        else:
            dashas = []
            maha_dasha = ""
            antar_dasha = ""

        # Aspects and conjunctions.
        aspects, planet_aspects = self._compute_aspects(planets)
        for name, pos in planets.items():
            pos.aspects = planet_aspects.get(name, [])
            pos.conjunctions = self._compute_conjunctions(planets, name)

        # Yogas and doshas.
        yoga_dicts = detect_yogas(planets, lagna_lon)
        dosha_dicts = detect_doshas(planets, lagna_lon)

        # Transits.
        transits = self._compute_transits(utc_dt)

        # Sun and Moon signs.
        sun_pos = planets.get("Sun")
        moon_pos = planets.get("Moon")

        return ChartData(
            chart_type=chart_type,
            lagna=zodiac_sign(lagna_lon),
            lagna_degree=round(sign_degree(lagna_lon), 4),
            lagna_nakshatra=get_nakshatra(lagna_lon),
            moon_sign=moon_pos.sign if moon_pos else "",
            sun_sign=sun_pos.sign if sun_pos else "",
            maha_dasha=maha_dasha,
            antar_dasha=antar_dasha,
            planets=dict(planets),
            houses={str(h.house): h for h in houses},
            nakshatras=nakshatras,
            dashas=[self._dash_dict(d) for d in dashas],
            yogas=[self._yoga_dict(y) for y in yoga_dicts],
            doshas=[self._dosha_dict(d) for d in dosha_dicts],
            aspects=aspects,
            transits=transits,
            generated_at=utc_dt.isoformat(),
        )

    def generate_varga(
        self,
        date_of_birth: str,
        time_of_birth: str | None,
        latitude: float,
        longitude: float,
        timezone: str,
        chart_type: str,
    ) -> VargaChart:
        """Generate a divisional chart (varga)."""
        if chart_type == "rashi":
            chart = self.generate(
                date_of_birth,
                time_of_birth,
                latitude,
                longitude,
                timezone,
                chart_type,
            )
            return VargaChart(
                chart_type=chart_type,
                lagna=chart.lagna,
                lagna_degree=chart.lagna_degree,
                planets=chart.planets,
                houses=chart.houses,
            )

        if chart_type == "navamsa":
            utc_dt = parse_birth_datetime(date_of_birth, time_of_birth, timezone)
            jd = julian_day(utc_dt)
            lagna_lon = self._compute_lagna(jd, latitude, longitude)
            planets = self._compute_planets(jd, lagna_lon, chart_type="navamsa")
            houses = self._compute_houses(planets, lagna_lon, "navamsa")
            return VargaChart(
                chart_type=chart_type,
                lagna=get_varga_sign(lagna_lon, "navamsa"),
                lagna_degree=round(sign_degree(lagna_lon), 4),
                planets=planets,
                houses={str(h.house): h for h in houses},
            )

        raise ValueError(f"Divisional chart '{chart_type}' is not yet implemented")

    def _compute_houses(
        self,
        planets: dict[str, PlanetPosition],
        lagna_lon: float,
        chart_type: str = "rashi",
    ) -> list[HousePosition]:
        from divyadrishti.astrology.constants import (
            HOUSE_BENEFIC,
            HOUSE_KENDRA,
            HOUSE_MALEFIC,
            HOUSE_MEANINGS,
            HOUSE_TRINITY,
            HOUSE_UPACHAYA,
        )

        if chart_type == "navamsa":
            lagna_sign = get_varga_sign(lagna_lon, "navamsa")
            lagna_sign_idx = SIGN_NAMES.index(lagna_sign)
        else:
            lagna_sign_idx = zodiac_sign_index(lagna_lon)
            lagna_sign = zodiac_sign(lagna_lon)
        houses = []
        for i in range(1, 13):
            sign_idx = (lagna_sign_idx + i - 1) % 12
            sign = SIGN_NAMES[sign_idx]
            house_lord = SIGN_LORDS[sign]
            occupying = [p.name for p in planets.values() if p.house == i]
            aspected_by = []
            for p in planets.values():
                distance = ((i - p.house) % 12) or 12
                if distance in ASPECT_HOUSES.get(p.name, {7}):
                    aspected_by.append(p.name)
            houses.append(
                HousePosition(
                    house=i,
                    sign=sign,
                    lord=house_lord,
                    planets=occupying,
                    aspected_by=aspected_by,
                    meaning=HOUSE_MEANINGS[i],
                    trinity=HOUSE_TRINITY[i],
                    is_kendra=i in HOUSE_KENDRA,
                    is_upachaya=i in HOUSE_UPACHAYA,
                    is_malefic=i in HOUSE_MALEFIC,
                    is_benefic=i in HOUSE_BENEFIC,
                )
            )
        return houses

    def _compute_nakshatra_details(
        self, planets: dict[str, PlanetPosition]
    ) -> dict[str, NakshatraDetail]:
        """Return detailed nakshatra info for each planet."""
        details: dict[str, NakshatraDetail] = {}
        for name, pos in planets.items():
            details[name] = NakshatraDetail(
                name=pos.nakshatra,
                pada=pos.nakshatra_pada,
                lord=pos.nakshatra_lord,
                planet=name,
                longitude=pos.longitude,
                characteristics=f"{pos.nakshatra} is ruled by {pos.nakshatra_lord} and falls in {pos.sign}.",
                current_influence=f"{name} in {pos.nakshatra} pada {pos.nakshatra_pada} influences {pos.house}th house matters.",
            )
        return details

    def _compute_aspects(self, planets: dict[str, PlanetPosition]) -> tuple[list[AspectDetail], dict[str, list[str]]]:
        from divyadrishti.astrology.aspects import calculate_aspects

        # Recompute using dynamic lagna: use Sun's house as approximate lagna for navamsa
        # if we do not have a lagna, otherwise use Moon's position.
        lagna_lon = 0.0
        for p in planets.values():
            if p.house == 1:
                lagna_lon = p.longitude
                break
        if lagna_lon == 0.0 and planets:
            lagna_lon = next(iter(planets.values())).longitude
        return calculate_aspects(planets, lagna_lon)

    def _compute_conjunctions(self, planets: dict[str, PlanetPosition], name: str) -> list[str]:
        pos = planets.get(name)
        if not pos:
            return []
        conjunctions = []
        for other_name, other_pos in planets.items():
            if other_name == name:
                continue
            if pos.sign == other_pos.sign:
                conjunctions.append(other_name)
        return conjunctions

    def _compute_transits(self, reference_dt: datetime) -> list[TransitPosition]:
        """Return current transits for the major planets."""
        jd = julian_day(reference_dt)
        transits = []
        for name in VALID_PLANETS:
            if name == "Ketu":
                rahu_res, _ = swe.calc_ut(jd, PLANET_SWISS_IDS["Rahu"], DEFAULT_FLAGS)
                lon = (rahu_res[0] + 180.0) % 360.0
            else:
                swiss_id = PLANET_SWISS_IDS[name]
                res, _ = swe.calc_ut(jd, swiss_id, DEFAULT_FLAGS)
                lon = res[0]
            sign = zodiac_sign(lon)
            # Transit houses are relative to the birth lagna? We don't have birth lagna here.
            # Use sign as a 1-based house relative to Aries for display.
            transits.append(
                TransitPosition(
                    name=name,
                    sign=sign,
                    house=zodiac_sign_index(lon) + 1,
                    longitude=round(lon, 4),
                    nakshatra=get_nakshatra(lon),
                    retrograde=self._is_retrograde(name, jd),
                )
            )
        return transits

    def _dash_dict(self, d: dict[str, Any]) -> DashaPeriod:
        return DashaPeriod(
            planet=d["planet"],
            start_date=d["start_date"],
            end_date=d["end_date"],
            is_current=d["is_current"],
            major_themes=[f"Themes of {d['planet']}"],
            relevant_planets=[d["planet"]],
        )

    def _yoga_dict(self, y: dict[str, Any]) -> YogaDetail:
        return YogaDetail(
            name=y["name"],
            strength=y["strength"],
            description=y["description"],
            conditions=y["conditions"],
            matched_conditions=y["matched_conditions"],
            current_relevance=y["current_relevance"],
            references=y["references"],
        )

    def _dosha_dict(self, d: dict[str, Any]) -> DoshaDetail:
        return DoshaDetail(
            name=d["name"],
            severity=d["severity"],
            conditions=d["conditions"],
            mitigating_factors=d["mitigating_factors"],
            confidence=d["confidence"],
            references=d["references"],
        )
