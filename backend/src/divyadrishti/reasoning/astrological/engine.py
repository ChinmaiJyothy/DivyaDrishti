"""Astrological Reasoning Engine orchestrator."""

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from divyadrishti.knowledge.hybrid_retrieval import CorpusRetrievalEngine


class AstrologicalReasoningEngine:
    """Transform birth chart, question, and knowledge rules into structured reasoning.

    Optionally accepts a ``corpus_engine`` (Knowledge Corpus hybrid
    retrieval). When supplied, approved corpus rules are merged with the
    file-based rule repository before evidence evaluation, and supporting
    verses/chapters are attached to the result for the Explainability
    Engine. This is fully backward compatible: omitting ``corpus_engine``
    preserves the original file-based-only behavior.
    """

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
        corpus_engine: "CorpusRetrievalEngine | None" = None,
        corpus_ids: list[int] | None = None,
    ) -> None:
        self.question_analyzer = question_analyzer or QuestionAnalyzer()
        self.rule_matcher = rule_matcher or RuleMatcher(knowledge_engine)
        self.evidence_evaluator = evidence_evaluator or EvidenceEvaluator()
        self.conflict_resolver = conflict_resolver or ConflictResolver()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self.reasoning_aggregator = reasoning_aggregator or ReasoningAggregator()
        self.reasoning_serializer = reasoning_serializer or ReasoningSerializer()
        self.corpus_engine = corpus_engine
        self.corpus_ids = corpus_ids

    def reason(self, request: ReasoningRequest) -> ReasoningResult:
        """Run the full astrological reasoning pipeline."""
        domain, factors, follow_up = self.question_analyzer.analyze(
            request.question, request.chart
        )

        rules = self.rule_matcher.find_rules(factors)

        corpus_references: list[dict] = []
        corpus_related_chapters: list[str] = []
        corpus_retrieval_method = "disabled"

        if self.corpus_engine is not None:
            corpus_result = self.corpus_engine.retrieve(
                request.question, factors, corpus_ids=self.corpus_ids
            )
            existing_ids = {r.rule_id for r in rules}
            for corpus_rule in corpus_result.rules:
                if corpus_rule.rule_id not in existing_ids:
                    rules.append(corpus_rule)
                    existing_ids.add(corpus_rule.rule_id)
            corpus_references = [ref.model_dump() for ref in corpus_result.supporting_verses]
            corpus_related_chapters = corpus_result.related_chapters
            corpus_retrieval_method = corpus_result.retrieval_method

        evidence = self.evidence_evaluator.evaluate(
            rules, request.chart, request.question
        )

        supporting, conflicting = self.conflict_resolver.resolve(evidence, request.question)

        overall_confidence = self.confidence_calculator.calculate(supporting, conflicting)

        result = self.reasoning_aggregator.aggregate(
            question=request.question,
            domain=domain,
            relevant_factors=factors,
            evidence=evidence,
            supporting=supporting,
            conflicting=conflicting,
            overall_confidence=overall_confidence,
            follow_up_topics=follow_up,
        )
        result.corpus_references = corpus_references
        result.corpus_related_chapters = corpus_related_chapters
        result.corpus_retrieval_method = corpus_retrieval_method
        return result

    def reason_trace(self, request: ReasoningRequest) -> ReasoningTrace:
        """Return the result serialized as a ReasoningTrace."""
        return self.reasoning_serializer.serialize(self.reason(request))
