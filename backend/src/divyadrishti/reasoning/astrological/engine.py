"""Astrological Reasoning Engine orchestrator."""

from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.reasoning.astrological.confidence_calculator import ConfidenceCalculator
from divyadrishti.reasoning.astrological.conflict_resolver import ConflictResolver
from divyadrishti.reasoning.astrological.evidence_evaluator import EvidenceEvaluator
from divyadrishti.reasoning.astrological.models import ReasoningRequest, ReasoningResult
from divyadrishti.reasoning.astrological.question_analyzer import QuestionAnalyzer
from divyadrishti.reasoning.astrological.reasoning_aggregator import ReasoningAggregator
from divyadrishti.reasoning.astrological.reasoning_serializer import ReasoningSerializer
from divyadrishti.reasoning.astrological.rule_matcher import RuleMatcher
from divyadrishti.reasoning.models import ReasoningTrace


class AstrologicalReasoningEngine:
    """Transform birth chart, question, and knowledge rules into structured reasoning."""

    def __init__(
        self,
        knowledge_engine: KnowledgeRetrievalEngine,
        question_analyzer: QuestionAnalyzer | None = None,
        rule_matcher: RuleMatcher | None = None,
        evidence_evaluator: EvidenceEvaluator | None = None,
        conflict_resolver: ConflictResolver | None = None,
        confidence_calculator: ConfidenceCalculator | None = None,
        reasoning_aggregator: ReasoningAggregator | None = None,
        reasoning_serializer: ReasoningSerializer | None = None,
    ) -> None:
        self.question_analyzer = question_analyzer or QuestionAnalyzer()
        self.rule_matcher = rule_matcher or RuleMatcher(knowledge_engine)
        self.evidence_evaluator = evidence_evaluator or EvidenceEvaluator()
        self.conflict_resolver = conflict_resolver or ConflictResolver()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self.reasoning_aggregator = reasoning_aggregator or ReasoningAggregator()
        self.reasoning_serializer = reasoning_serializer or ReasoningSerializer()

    def reason(self, request: ReasoningRequest) -> ReasoningResult:
        """Run the full astrological reasoning pipeline."""
        domain, factors, follow_up = self.question_analyzer.analyze(
            request.question, request.chart
        )

        rules = self.rule_matcher.find_rules(factors)

        evidence = self.evidence_evaluator.evaluate(
            rules, request.chart, request.question
        )

        supporting, conflicting = self.conflict_resolver.resolve(evidence, request.question)

        overall_confidence = self.confidence_calculator.calculate(supporting, conflicting)

        return self.reasoning_aggregator.aggregate(
            question=request.question,
            domain=domain,
            relevant_factors=factors,
            evidence=evidence,
            supporting=supporting,
            conflicting=conflicting,
            overall_confidence=overall_confidence,
            follow_up_topics=follow_up,
        )

    def reason_trace(self, request: ReasoningRequest) -> ReasoningTrace:
        """Return the result serialized as a ReasoningTrace."""
        return self.reasoning_serializer.serialize(self.reason(request))
