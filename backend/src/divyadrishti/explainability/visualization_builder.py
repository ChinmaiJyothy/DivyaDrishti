"""Visualization Builder for the Explainability Engine."""

from divyadrishti.explainability.models import ReasoningGraph, VisualizationData
from divyadrishti.reasoning.astrological.models import AstrologicalChart, ReasoningResult


class VisualizationBuilder:
    """Build frontend-ready visualization data structures."""

    def build(
        self,
        chart: AstrologicalChart,
        result: ReasoningResult,
        graph: ReasoningGraph,
    ) -> VisualizationData:
        """Build all visualizations from chart, result, and reasoning graph."""
        return VisualizationData(
            decision_tree=self._build_decision_tree(graph),
            reasoning_timeline=self._build_reasoning_timeline(graph),
            evidence_tree=self._build_evidence_tree(result),
            planet_influence_graph=self._build_planet_influence_graph(chart),
            house_influence_graph=self._build_house_influence_graph(chart),
            knowledge_source_graph=self._build_knowledge_source_graph(result),
        )

    def _build_decision_tree(self, graph: ReasoningGraph) -> dict:
        return {"root": graph.root.model_dump()}

    def _build_reasoning_timeline(self, graph: ReasoningGraph) -> list[dict]:
        timeline = []

        def traverse(node, depth=0):
            timeline.append({"id": node.id, "label": node.label, "type": node.type, "depth": depth})
            for child in node.children:
                traverse(child, depth + 1)

        traverse(graph.root)
        return timeline

    def _build_evidence_tree(self, result: ReasoningResult) -> dict:
        return {
            "root": "Evidence",
            "supporting": [
                {"rule_id": ev.rule_id, "confidence": ev.confidence, "weight": ev.weight}
                for ev in result.supporting_evidence
            ],
            "conflicting": [
                {"rule_id": ev.rule_id, "confidence": ev.confidence, "weight": ev.weight}
                for ev in result.conflicting_evidence
            ],
        }

    def _build_planet_influence_graph(self, chart: AstrologicalChart) -> dict:
        nodes = [{"id": planet, "type": "planet", "label": planet} for planet in chart.planets]
        edges = []
        for planet, data in chart.planets.items():
            house = data.get("house")
            sign = data.get("sign")
            if house is not None:
                edges.append({"source": planet, "target": f"house_{house}", "type": "occupies"})
            if sign:
                edges.append({"source": planet, "target": f"sign_{sign}", "type": "in_sign"})
        return {"nodes": nodes, "edges": edges}

    def _build_house_influence_graph(self, chart: AstrologicalChart) -> dict:
        nodes = [{"id": f"house_{h}", "type": "house", "label": f"House {h}"} for h in range(1, 13)]
        edges = []
        for planet, data in chart.planets.items():
            house = data.get("house")
            if house is not None:
                edges.append({"source": f"house_{house}", "target": planet, "type": "contains"})
        return {"nodes": nodes, "edges": edges}

    def _build_knowledge_source_graph(self, result: ReasoningResult) -> dict:
        sources: dict[str, list[str]] = {}
        for ev in result.matched_rules + result.partially_matched_rules + result.unmatched_rules:
            sources.setdefault(ev.source, []).append(ev.rule_id)

        nodes = [{"id": book, "type": "book"} for book in sources]
        nodes += [{"id": rule_id, "type": "rule"} for rule_id in sum(sources.values(), [])]
        edges = []
        for book, rule_ids in sources.items():
            for rule_id in rule_ids:
                edges.append({"source": book, "target": rule_id})
        return {"nodes": nodes, "edges": edges}
