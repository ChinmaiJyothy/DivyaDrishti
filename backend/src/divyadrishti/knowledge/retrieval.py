"""Knowledge Retrieval Engine for querying Vedic astrology rules."""

from divyadrishti.knowledge.models import Rule
from divyadrishti.knowledge.repository import KnowledgeRepository


class KnowledgeRetrievalEngine:
    """Retrieve rules by topic, house, planet, yoga, dosha, dasha, source, or combination."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def _all_rules(self) -> list[Rule]:
        return self.repository.list_rules(enabled_only=True)

    def retrieve_by_topic(self, topic: str) -> list[Rule]:
        return [rule for rule in self._all_rules() if rule.topic.lower() == topic.lower()]

    def retrieve_by_house(self, house: int) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if house in rule.astrological_factors.houses
        ]

    def retrieve_by_planet(self, planet: str) -> list[Rule]:
        planet = planet.capitalize()
        return [
            rule
            for rule in self._all_rules()
            if planet in rule.astrological_factors.planets
        ]

    def retrieve_by_sign(self, sign: str) -> list[Rule]:
        sign = sign.capitalize()
        return [
            rule
            for rule in self._all_rules()
            if sign in rule.astrological_factors.signs
        ]

    def retrieve_by_nakshatra(self, nakshatra: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if nakshatra in rule.astrological_factors.nakshatras
        ]

    def retrieve_by_yoga(self, yoga: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if yoga in rule.astrological_factors.yogas
        ]

    def retrieve_by_dosha(self, dosha: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if dosha in rule.astrological_factors.doshas
        ]

    def retrieve_by_dasha(self, dasha: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if dasha in rule.astrological_factors.dashas
        ]

    def retrieve_by_chapter(self, chapter: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if rule.chapter and rule.chapter.lower() == chapter.lower()
        ]

    def retrieve_by_source(self, source_book: str) -> list[Rule]:
        return [
            rule
            for rule in self._all_rules()
            if rule.source_book.lower() == source_book.lower()
        ]

    def retrieve_by_combination(self, factors: dict) -> list[Rule]:
        """Retrieve rules that match all provided astrological factors.

        Example factors: {"houses": [7], "planets": ["Jupiter"]}
        """
        results = []
        for rule in self._all_rules():
            score = self._score_rule(rule, factors)
            if score > 0:
                results.append((rule, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [rule for rule, _ in results]

    def retrieve_by_query(self, query: str) -> list[Rule]:
        """Simple keyword search across topic, interpretation, and tags."""
        query = query.lower()
        results = []
        for rule in self._all_rules():
            score = 0
            text = " ".join(
                [
                    rule.topic,
                    rule.subtopic or "",
                    rule.interpretation,
                    rule.supporting_notes or "",
                    " ".join(rule.tags),
                    " ".join(rule.conditions),
                ]
            ).lower()
            if query in text:
                score += text.count(query)
                results.append((rule, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [rule for rule, _ in results]

    def _score_rule(self, rule: Rule, factors: dict) -> int:
        score = 0
        rule_factors = rule.astrological_factors

        for key, values in factors.items():
            if not values:
                continue
            rule_values = getattr(rule_factors, key, [])
            if not isinstance(values, (list, set, tuple)):
                values = [values]
            matched = set(values) & set(rule_values)
            score += len(matched)

        return score

    def retrieve_for_reasoning(self, chart: dict, question: str) -> list[Rule]:
        """Retrieve rules relevant to a birth chart and a user question.

        This is a placeholder that will be expanded by the Reasoning Engine.
        """
        results: list[Rule] = []
        keywords = [word.lower() for word in question.split()]
        for rule in self._all_rules():
            text = f"{rule.topic} {rule.subtopic or ''} {rule.interpretation}"
            if any(keyword in text.lower() for keyword in keywords):
                results.append(rule)
        return results
