"""Studio service for interactive birth chart exploration."""

from typing import Any

from sqlalchemy.orm import Session

from divyadrishti.astrology.models import (
    ChartData,
    ChartStudioDetail,
    InsightHighlight,
    StudioInsight,
)
from divyadrishti.astrology.utils import to_astrological_chart
from divyadrishti.explainability.engine import ExplainabilityEngine
from divyadrishti.knowledge.repository import KnowledgeRepository
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.reasoning.astrological.engine import AstrologicalReasoningEngine
from divyadrishti.reasoning.astrological.models import ReasoningRequest, ReasoningResult
from divyadrishti.services.birth_chart_service import BirthChartService


class StudioService:
    """Orchestrate chart data, reasoning, explainability, and knowledge for the studio."""

    def __init__(self, db: Session, knowledge_repository: KnowledgeRepository | None = None) -> None:
        self.db = db
        self.knowledge_repository = knowledge_repository
        self.chart_service = BirthChartService(db)
        self.knowledge_engine = (
            KnowledgeRetrievalEngine(knowledge_repository) if knowledge_repository else None
        )

    def get_studio_detail(
        self,
        chart_id: int,
        user_id: int,
        question: str | None = None,
    ) -> ChartStudioDetail:
        """Return the full studio detail for a chart."""
        chart = self.chart_service.get_by_id(chart_id, user_id)
        if not chart:
            raise ValueError("Chart not found")

        chart_data = ChartData.model_validate(chart.chart_data)
        astrological_chart = to_astrological_chart(chart_data)
        query = question or "Analyze the chart"

        if self.knowledge_repository and self.knowledge_engine:
            knowledge_engine = self.knowledge_engine
            reasoning_engine = AstrologicalReasoningEngine(knowledge_engine)
            reasoning_result = reasoning_engine.reason(
                ReasoningRequest(question=query, chart=astrological_chart)
            )
            explainability_engine = ExplainabilityEngine(self.knowledge_repository)
            explainability_report = explainability_engine.explain(
                query, astrological_chart, reasoning_result
            )
            visualizations = explainability_report.visualizations.model_dump()
            insight = self._build_insight(query, chart_data, reasoning_result)
        else:
            visualizations = {}
            insight = self._build_insight(query, chart_data, None)

        return ChartStudioDetail(
            chart_id=chart.id,
            profile_id=chart.profile_id,
            chart_type=chart.chart_type,
            lagna=chart_data.lagna,
            lagna_degree=chart_data.lagna_degree,
            moon_sign=chart_data.moon_sign,
            sun_sign=chart_data.sun_sign,
            maha_dasha=chart_data.maha_dasha,
            antar_dasha=chart_data.antar_dasha,
            planets=chart_data.planets,
            houses=chart_data.houses,
            nakshatras=chart_data.nakshatras,
            dashas=chart_data.dashas,
            yogas=chart_data.yogas,
            doshas=chart_data.doshas,
            aspects=chart_data.aspects,
            transits=chart_data.transits,
            visualizations=visualizations,
            insight=insight,
            generated_at=chart_data.generated_at,
        )

    def search_chart(self, chart_id: int, user_id: int, query: str) -> list[dict[str, Any]]:
        """Search across chart elements for a query string."""
        chart = self.chart_service.get_by_id(chart_id, user_id)
        if not chart:
            raise ValueError("Chart not found")

        chart_data = ChartData.model_validate(chart.chart_data)
        query_lower = query.lower()
        results = []

        for name, pos in chart_data.planets.items():
            text = f"{name} {pos.sign} {pos.nakshatra} {pos.dignity} {pos.house}"
            if query_lower in text.lower():
                results.append(
                    {"type": "planet", "id": name, "label": f"{name} in {pos.sign}", "reason": text}
                )

        for house in chart_data.houses.values():
            text = f"{house.house} {house.sign} {house.lord} {house.meaning}"
            if query_lower in text.lower():
                results.append(
                    {"type": "house", "id": str(house.house), "label": f"House {house.house}", "reason": text}
                )

        for nak in chart_data.nakshatras.values():
            if query_lower in nak.name.lower() or query_lower in nak.lord.lower():
                results.append(
                    {"type": "nakshatra", "id": nak.name, "label": nak.name, "reason": f"{nak.name} lord {nak.lord}"}
                )

        for yoga in chart_data.yogas:
            if query_lower in yoga.name.lower() or query_lower in yoga.description.lower():
                results.append(
                    {"type": "yoga", "id": yoga.name, "label": yoga.name, "reason": yoga.description}
                )

        for dosha in chart_data.doshas:
            conditions_match = any(query_lower in c.lower() for c in dosha.conditions)
            if query_lower in dosha.name.lower() or conditions_match:
                results.append(
                    {"type": "dosha", "id": dosha.name, "label": dosha.name, "reason": dosha.conditions[0] if dosha.conditions else ""}
                )

        for dasha in chart_data.dashas:
            if query_lower in dasha.planet.lower():
                results.append(
                    {"type": "dasha", "id": dasha.planet, "label": f"{dasha.planet} dasha", "reason": f"{dasha.start_date} - {dasha.end_date}"}
                )

        return results

    def _build_insight(
        self,
        question: str,
        chart_data: ChartData,
        reasoning_result: ReasoningResult | None,
    ) -> StudioInsight:
        """Create a context-aware insight summary for the given question."""
        topic = self._detect_topic(question)
        highlights = []

        if topic == "career":
            highlights = self._highlight_career(chart_data)
        elif topic == "marriage":
            highlights = self._highlight_marriage(chart_data)
        elif topic == "finance":
            highlights = self._highlight_finance(chart_data)
        elif topic == "health":
            highlights = self._highlight_health(chart_data)
        else:
            highlights = self._highlight_general(chart_data)

        if reasoning_result and reasoning_result.relevant_factors:
            factors = reasoning_result.relevant_factors
            for planet in factors.planets:
                if planet in chart_data.planets:
                    highlights.append(
                        InsightHighlight(
                            type="planet",
                            id=planet,
                            label=planet,
                            reason="Relevant factor for the question",
                        )
                    )
            for house in factors.houses:
                if str(house) in chart_data.houses:
                    highlights.append(
                        InsightHighlight(
                            type="house",
                            id=str(house),
                            label=f"House {house}",
                            reason="Relevant factor for the question",
                        )
                    )

        summary = f"The chart is being analyzed for {topic}. Key highlights are listed above."
        return StudioInsight(
            topic=topic,
            highlights=highlights,
            summary=summary,
            recommendations=[
                "Explore highlighted planets and houses for detailed interpretation.",
                "Use the reasoning graph to see how classical rules apply.",
            ],
        )

    def _detect_topic(self, question: str) -> str:
        q = question.lower()
        if any(k in q for k in ("career", "profession", "job", "work", "business")):
            return "career"
        if any(k in q for k in ("marriage", "spouse", "love", "partner", "relationship", "7th")):
            return "marriage"
        if any(k in q for k in ("money", "finance", "wealth", "income", "property")):
            return "finance"
        if any(k in q for k in ("health", "disease", "body", "illness")):
            return "health"
        return "general"

    def _highlight_career(self, chart_data: ChartData) -> list[InsightHighlight]:
        highlights = []
        if "10" in chart_data.houses:
            h = chart_data.houses["10"]
            highlights.append(
                InsightHighlight(type="house", id="10", label="10th House", reason="Primary house for career and status")
            )
            for p in h.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Occupies 10th house of career")
                )
        for p in ["Saturn", "Sun"]:
            if p in chart_data.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Key planet for career and authority")
                )
        for yoga in chart_data.yogas:
            if yoga.name in {"Raja Yoga", "Dhana Yoga"}:
                highlights.append(
                    InsightHighlight(type="yoga", id=yoga.name, label=yoga.name, reason="Relevant for career success")
                )
        if chart_data.dashas:
            current = next((d for d in chart_data.dashas if d.is_current), chart_data.dashas[0])
            highlights.append(
                InsightHighlight(type="dasha", id=current.planet, label=current.planet, reason="Current dasha influencing career timing")
            )
        return highlights

    def _highlight_marriage(self, chart_data: ChartData) -> list[InsightHighlight]:
        highlights = []
        if "7" in chart_data.houses:
            h = chart_data.houses["7"]
            highlights.append(
                InsightHighlight(type="house", id="7", label="7th House", reason="Primary house for marriage and partnership")
            )
            for p in h.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Influences 7th house of relationships")
                )
        for p in ["Venus", "Jupiter"]:
            if p in chart_data.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Key planet for marriage and harmony")
                )
        if chart_data.planets and "Moon" in chart_data.planets:
            moon = chart_data.planets["Moon"]
            highlights.append(
                InsightHighlight(type="sign", id=moon.navamsa_sign or "", label=moon.navamsa_sign or "", reason="Navamsa position for marriage")
            )
        return highlights

    def _highlight_finance(self, chart_data: ChartData) -> list[InsightHighlight]:
        highlights = []
        for house_id in ["2", "11"]:
            if house_id in chart_data.houses:
                highlights.append(
                    InsightHighlight(type="house", id=house_id, label=f"House {house_id}", reason="Wealth and gains")
                )
        for p in ["Venus", "Jupiter", "Mercury"]:
            if p in chart_data.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Financial significator")
                )
        return highlights

    def _highlight_health(self, chart_data: ChartData) -> list[InsightHighlight]:
        highlights = []
        if "1" in chart_data.houses:
            highlights.append(
                InsightHighlight(type="house", id="1", label="1st House", reason="Body and vitality")
            )
        if "6" in chart_data.houses:
            highlights.append(
                InsightHighlight(type="house", id="6", label="6th House", reason="Disease and obstacles")
            )
        for p in ["Sun", "Moon", "Mars", "Saturn"]:
            if p in chart_data.planets:
                highlights.append(
                    InsightHighlight(type="planet", id=p, label=p, reason="Health significator")
                )
        return highlights

    def _highlight_general(self, chart_data: ChartData) -> list[InsightHighlight]:
        highlights = [InsightHighlight(type="house", id="1", label="1st House", reason="Lagna and overall self")]
        if chart_data.planets:
            moon = chart_data.planets.get("Moon")
            if moon:
                highlights.append(
                    InsightHighlight(type="planet", id="Moon", label="Moon", reason=f"Mind in {moon.sign}")
                )
            sun = chart_data.planets.get("Sun")
            if sun:
                highlights.append(
                    InsightHighlight(type="planet", id="Sun", label="Sun", reason=f"Soul in {sun.sign}")
                )
        return highlights
