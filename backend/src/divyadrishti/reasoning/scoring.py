"""Scoring and matching logic for evidence evaluation."""

from divyadrishti.knowledge.models import AstrologicalFactors, Rule
from divyadrishti.reasoning.models import ChartData, Evidence


def match_factors(factors: AstrologicalFactors, chart: ChartData) -> dict[str, list[str] | list[int]]:
    """Return the rule factors that are present in the chart.

    For rules that specify both houses and planets, the engine requires the
    planet to actually occupy one of the rule houses. This prevents false
    positives where a house is active but the requested planet is elsewhere.
    """
    matched: dict[str, list] = {}

    matched["house_planet"] = _match_house_planet_combinations(factors, chart)

    if factors.houses and factors.planets:
        # Strict conjunction: require planet-in-house.
        if matched["house_planet"]:
            matched_houses = sorted(set(factors.houses) & set(chart.active_houses))
            if matched_houses:
                matched["houses"] = matched_houses
            matched_planets = sorted(set(factors.planets) & set(chart.active_planets))
            if matched_planets:
                matched["planets"] = matched_planets
    else:
        matched_houses = sorted(set(factors.houses) & set(chart.active_houses))
        if matched_houses:
            matched["houses"] = matched_houses

        matched_planets = sorted(set(factors.planets) & set(chart.active_planets))
        if matched_planets:
            matched["planets"] = matched_planets

    matched_signs = sorted(set(factors.signs) & set(chart.active_signs))
    if matched_signs:
        matched["signs"] = matched_signs

    matched_nakshatras = sorted(set(factors.nakshatras) & set(chart.active_nakshatras))
    if matched_nakshatras:
        matched["nakshatras"] = matched_nakshatras

    matched_yogas = sorted(set(factors.yogas) & set(chart.yogas))
    if matched_yogas:
        matched["yogas"] = matched_yogas

    matched_doshas = sorted(set(factors.doshas) & set(chart.doshas))
    if matched_doshas:
        matched["doshas"] = matched_doshas

    matched_dashas = sorted(set(factors.dashas) & set(chart.dashas))
    if matched_dashas:
        matched["dashas"] = matched_dashas

    matched_topics = sorted(set(factors.topics) & set(chart.topics))
    if matched_topics:
        matched["topics"] = matched_topics

    if not matched["house_planet"]:
        del matched["house_planet"]

    return matched


def _match_house_planet_combinations(factors: AstrologicalFactors, chart: ChartData) -> list[str]:
    """Detect specific planet-in-house placements requested by the rule."""
    if not factors.houses or not factors.planets:
        return []

    matches: list[str] = []
    for planet in factors.planets:
        position = chart.planets.get(planet)
        if position and position.house in factors.houses:
            matches.append(f"{planet} in house {position.house}")
    return matches


def compute_confidence(rule: Rule, matched: dict[str, list]) -> float:
    """Compute an evidence confidence score between 0 and 100."""
    if not matched:
        return 0.0

    factor_count = sum(len(values) for values in matched.values())
    base_confidence = rule.confidence * 100
    return round(min(100.0, base_confidence * (1 + 0.1 * factor_count)), 2)


def compute_weight(rule: Rule, matched: dict[str, list]) -> float:
    """Compute an evidence weight based on rule confidence and matched factors."""
    factor_count = sum(len(values) for values in matched.values())
    return round(rule.confidence * factor_count, 2)


def build_matched_conditions(matched: dict[str, list]) -> list[str]:
    """Build human-readable matched condition statements."""
    conditions: list[str] = []
    for key, values in matched.items():
        if not values:
            continue
        if key == "house_planet":
            for value in values:
                conditions.append(f"Matched {value}")
        else:
            label = key.capitalize()
            conditions.append(f"Matched {label}: {', '.join(str(v) for v in values)}")
    return conditions


def build_evidence(rule: Rule, chart: ChartData, matched: dict[str, list]) -> Evidence:
    """Build a full Evidence object from a matched rule."""
    confidence = compute_confidence(rule, matched)
    weight = compute_weight(rule, matched)
    matched_conditions = build_matched_conditions(matched)
    notes = f"Matched factors: {matched}." if matched else "No astrological factors matched."

    return Evidence(
        rule_id=rule.rule_id,
        source=rule.source_book,
        conditions=rule.conditions,
        matched_conditions=matched_conditions,
        confidence=confidence,
        weight=weight,
        explanation=rule.interpretation,
        notes=notes,
    )
