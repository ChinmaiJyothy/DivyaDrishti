"""Rule Matcher for retrieving relevant knowledge rules."""

from divyadrishti.knowledge.models import Rule
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.reasoning.astrological.models import AstrologicalEntity


class RuleMatcher:
    """Retrieve rules that match the relevant astrological entities."""

    def __init__(self, knowledge_engine: KnowledgeRetrievalEngine) -> None:
        self.knowledge_engine = knowledge_engine

    def find_rules(self, entities: AstrologicalEntity) -> list[Rule]:
        """Return a deduplicated list of relevant rules."""
        candidates: list[Rule] = []

        combination = self._build_combination(entities)
        if combination:
            candidates.extend(self.knowledge_engine.retrieve_by_combination(combination))

        for house in entities.houses:
            candidates.extend(self.knowledge_engine.retrieve_by_house(house))

        for planet in entities.planets:
            candidates.extend(self.knowledge_engine.retrieve_by_planet(planet))

        for topic in entities.topics:
            candidates.extend(self.knowledge_engine.retrieve_by_topic(topic))

        for yoga in entities.yogas:
            candidates.extend(self.knowledge_engine.retrieve_by_yoga(yoga))

        for dosha in entities.doshas:
            candidates.extend(self.knowledge_engine.retrieve_by_dosha(dosha))

        for dasha in entities.dashas:
            candidates.extend(self.knowledge_engine.retrieve_by_dasha(dasha))

        return self._deduplicate(candidates)

    def _build_combination(self, entities: AstrologicalEntity) -> dict[str, list]:
        combination: dict[str, list] = {}
        if entities.houses:
            combination["houses"] = entities.houses
        if entities.planets:
            combination["planets"] = entities.planets
        if entities.dashas:
            combination["dashas"] = entities.dashas
        return combination

    def _deduplicate(self, rules: list[Rule]) -> list[Rule]:
        seen: set[str] = set()
        unique: list[Rule] = []
        for rule in rules:
            if rule.rule_id not in seen:
                seen.add(rule.rule_id)
                unique.append(rule)
        return unique
