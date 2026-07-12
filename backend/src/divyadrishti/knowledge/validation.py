"""Rule validation logic."""

from pathlib import Path

from pydantic import ValidationError

from divyadrishti.knowledge.constants import (
    VALID_BOOKS,
    VALID_DASHAS,
    VALID_DOSHAS,
    VALID_HOUSES,
    VALID_NAKSHATRAS,
    VALID_PLANETS,
    VALID_SIGNS,
    VALID_YOGAS,
)
from divyadrishti.knowledge.exceptions import DuplicateRuleError, RuleValidationError
from divyadrishti.knowledge.models import Rule


class RuleValidator:
    """Validate imported rules against the schema and Vedic astrology domain rules."""

    def __init__(self) -> None:
        self.valid_planets = VALID_PLANETS
        self.valid_houses = VALID_HOUSES
        self.valid_signs = VALID_SIGNS
        self.valid_nakshatras = set(VALID_NAKSHATRAS)
        self.valid_yogas = set(VALID_YOGAS)
        self.valid_doshas = set(VALID_DOSHAS)
        self.valid_dashas = set(VALID_DASHAS)
        self.valid_books = set(VALID_BOOKS.keys()) | set(VALID_BOOKS.values())

    def validate(self, data: dict | Rule) -> Rule:
        """Validate a single rule."""
        if isinstance(data, Rule):
            rule = data
        else:
            try:
                rule = Rule.model_validate(data)
            except ValidationError as exc:
                rule_id = data.get("rule_id", "unknown")
                raise RuleValidationError(str(exc), rule_id=rule_id) from exc

        self._validate_domain_values(rule)
        return rule

    def validate_batch(self, rules: list[dict | Rule]) -> list[Rule]:
        """Validate a batch of rules and check for duplicate IDs."""
        seen: set[str] = set()
        validated: list[Rule] = []

        for item in rules:
            rule = self.validate(item)
            if rule.rule_id in seen:
                raise DuplicateRuleError(rule.rule_id)
            seen.add(rule.rule_id)
            validated.append(rule)

        return validated

    def _validate_domain_values(self, rule: Rule) -> None:
        factors = rule.astrological_factors

        for house in factors.houses:
            if house not in self.valid_houses:
                raise RuleValidationError(
                    f"Invalid house number: {house}. Expected 1-12.",
                    rule_id=rule.rule_id,
                )

        for planet in factors.planets:
            if planet not in self.valid_planets:
                raise RuleValidationError(
                    f"Invalid planet: {planet}",
                    rule_id=rule.rule_id,
                )

        for sign in factors.signs:
            if sign not in self.valid_signs:
                raise RuleValidationError(
                    f"Invalid sign: {sign}",
                    rule_id=rule.rule_id,
                )

        for nakshatra in factors.nakshatras:
            if nakshatra not in self.valid_nakshatras:
                raise RuleValidationError(
                    f"Invalid nakshatra: {nakshatra}",
                    rule_id=rule.rule_id,
                )

        for yoga in factors.yogas:
            if yoga not in self.valid_yogas:
                raise RuleValidationError(
                    f"Unrecognized yoga: {yoga}",
                    rule_id=rule.rule_id,
                )

        for dosha in factors.doshas:
            if dosha not in self.valid_doshas:
                raise RuleValidationError(
                    f"Unrecognized dosha: {dosha}",
                    rule_id=rule.rule_id,
                )

        for dasha in factors.dashas:
            if dasha not in self.valid_dashas:
                raise RuleValidationError(
                    f"Unrecognized dasha system: {dasha}",
                    rule_id=rule.rule_id,
                )

        if rule.source_book not in self.valid_books:
            raise RuleValidationError(
                f"Unknown source book: {rule.source_book}",
                rule_id=rule.rule_id,
            )

        if not rule.conditions:
            raise RuleValidationError(
                "Rule must have at least one condition.",
                rule_id=rule.rule_id,
            )

        if not rule.interpretation.strip():
            raise RuleValidationError(
                "Rule interpretation cannot be empty.",
                rule_id=rule.rule_id,
            )
