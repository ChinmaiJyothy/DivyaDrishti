"""Question Analyzer for the Astrological Reasoning Engine."""

from divyadrishti.reasoning.astrological.models import AstrologicalChart, AstrologicalEntity

DOMAIN_KEYWORDS = {
    "career": ["career", "profession", "job", "work", "business", "success", "status", "authority", "promotion"],
    "marriage": ["marriage", "married", "spouse", "wife", "husband", "partner", "wedding", "7th"],
    "health": ["health", "disease", "illness", "body", "sick", "life", "longevity"],
    "education": ["education", "study", "student", "exam", "learning", "school", "college"],
    "finance": ["money", "wealth", "finance", "income", "property", "gain", "loss", "debt"],
    "relationships": ["relationship", "love", "romance", "affair", "friend", "family"],
    "children": ["children", "child", "pregnancy", "progeny", "son", "daughter"],
    "travel": ["travel", "abroad", "foreign", "journey", "relocation", "migration"],
    "business": ["business", "entrepreneur", "venture", "trade", "commerce"],
    "spirituality": ["spiritual", "moksha", "dharma", "meditation", "god", "religion"],
    "personality": ["personality", "character", "nature", "mind", "behavior"],
    "general": [],
}

DOMAIN_ENTITIES = {
    "career": AstrologicalEntity(houses=[10], planets=["Saturn", "Sun", "Mercury"], topics=["career"]),
    "marriage": AstrologicalEntity(houses=[7], planets=["Venus", "Jupiter"], topics=["marriage"]),
    "health": AstrologicalEntity(houses=[1, 6, 8], planets=["Sun", "Moon", "Mars"], topics=["health"]),
    "education": AstrologicalEntity(houses=[4, 5, 9], planets=["Jupiter", "Mercury"], topics=["education"]),
    "finance": AstrologicalEntity(houses=[2, 11], planets=["Jupiter", "Mercury"], topics=["finance"]),
    "relationships": AstrologicalEntity(houses=[7, 5], planets=["Venus", "Jupiter"], topics=["relationships"]),
    "children": AstrologicalEntity(houses=[5], planets=["Jupiter", "Venus"], topics=["children"]),
    "travel": AstrologicalEntity(houses=[9, 12], planets=["Rahu", "Ketu"], topics=["travel"]),
    "business": AstrologicalEntity(houses=[7, 10], planets=["Mercury", "Jupiter"], topics=["business"]),
    "spirituality": AstrologicalEntity(houses=[9, 12], planets=["Jupiter", "Ketu"], topics=["spirituality"]),
    "personality": AstrologicalEntity(houses=[1, 5], planets=["Sun", "Moon"], topics=["personality"]),
    "general": AstrologicalEntity(),
}

FOLLOW_UP_TOPICS = {
    "career": [" Timing of promotion", "Business vs job", "Foreign career"],
    "marriage": [" Timing of marriage", "Spouse characteristics", "Marriage compatibility"],
    "health": ["Specific health concerns", "Remedial measures", "Longevity factors"],
    "finance": ["Sources of income", "Investment timing", "Debt repayment"],
    "relationships": ["Compatibility with partner", "Reasons for delay", "Family relationships"],
    "spirituality": ["Spiritual practices", "Moksha indications", "Guru guidance"],
    "general": ["Dasha analysis", "Yoga identification", "Remedial measures"],
}


class QuestionAnalyzer:
    """Analyze the user's question and chart to determine domain and relevant entities."""

    def analyze(self, question: str, chart: AstrologicalChart) -> tuple[str, AstrologicalEntity, list[str]]:
        """Return (domain, relevant_entities, follow_up_topics)."""
        domain = self._detect_domain(question)
        base_entities = DOMAIN_ENTITIES.get(domain, AstrologicalEntity())
        entities = self._enrich_with_chart(base_entities, chart)
        follow_up = FOLLOW_UP_TOPICS.get(domain, FOLLOW_UP_TOPICS["general"])
        return domain, entities, follow_up

    def _detect_domain(self, question: str) -> str:
        text = question.lower()
        scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[domain] += 1

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "general"
        return best

    def _enrich_with_chart(
        self, entities: AstrologicalEntity, chart: AstrologicalChart
    ) -> AstrologicalEntity:
        """Add current dasha and chart factors to the entity set."""
        dashas = list(entities.dashas)
        if chart.maha_dasha and chart.maha_dasha not in dashas:
            dashas.append(chart.maha_dasha)
        if chart.antar_dasha and chart.antar_dasha not in dashas:
            dashas.append(chart.antar_dasha)

        nakshatras = list(entities.nakshatras)
        for planet, data in chart.planets.items():
            if data.get("nakshatra") and data["nakshatra"] not in nakshatras:
                nakshatras.append(data["nakshatra"])

        return AstrologicalEntity(
            houses=entities.houses,
            planets=entities.planets,
            signs=entities.signs,
            nakshatras=nakshatras,
            yogas=chart.yogas + entities.yogas,
            doshas=chart.doshas + entities.doshas,
            dashas=dashas,
            topics=entities.topics,
        )
