"""Reasoning Graph Builder for the Explainability Engine."""

from divyadrishti.explainability.models import Node, ReasoningGraph
from divyadrishti.reasoning.astrological.models import ReasoningResult


class ReasoningGraphBuilder:
    """Build a traversable reasoning graph from a ReasoningResult."""

    def build(self, result: ReasoningResult) -> ReasoningGraph:
        """Build a reasoning graph including domain detection, rule retrieval, factor evaluation, and conclusion."""
        root = Node(id="question", label=f"Question: {result.question}", type="question")

        domain = Node(id="domain", label=f"Detect Domain: {result.domain}", type="domain")
        root.children.append(domain)

        retrieve = Node(id="retrieve_rules", label="Retrieve Relevant Rules", type="retrieve")
        domain.children.append(retrieve)

        factor_node = Node(id="evaluate_factors", label="Evaluate Chart Factors", type="evaluation")
        retrieve.children.append(factor_node)

        factors = result.relevant_factors
        factor_map = {
            "houses": factors.houses,
            "planets": factors.planets,
            "signs": factors.signs,
            "nakshatras": factors.nakshatras,
            "yogas": factors.yogas,
            "doshas": factors.doshas,
            "dashas": factors.dashas,
            "topics": factors.topics,
        }

        for factor_name, values in factor_map.items():
            if values:
                label = f"Evaluate {factor_name.capitalize()}: {', '.join(str(v) for v in values)}"
                factor_node.children.append(
                    Node(id=f"factor_{factor_name}", label=label, type="factor", metadata={factor_name: values})
                )

        if result.reasoning_steps:
            steps_node = Node(id="reasoning_steps", label="Reasoning Steps", type="steps")
            factor_node.children.append(steps_node)
            for i, step in enumerate(result.reasoning_steps, 1):
                steps_node.children.append(
                    Node(id=f"step_{i}", label=step.step, type="step", metadata={"details": step.details})
                )

        combine = Node(id="combine_evidence", label="Combine Evidence", type="combine")
        factor_node.children.append(combine)

        conclusion = Node(
            id="conclusion",
            label=f"Conclusion (Confidence: {result.overall_confidence:.1f}%)",
            type="conclusion",
            metadata={"summary": result.reasoning_summary},
        )
        combine.children.append(conclusion)

        return ReasoningGraph(root=root)
