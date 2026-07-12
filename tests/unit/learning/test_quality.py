from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.models import AstrologicalFactors, Rule
from divyadrishti.learning import FeedbackEntry, FeedbackManager, QualityAnalyzer


def test_quality_analyzer():
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    feedback = FeedbackManager()
    analyzer = QualityAnalyzer(repo, feedback)

    rule = repo.list_rules(enabled_only=True)
    if rule:
        metrics = analyzer.analyze(rule[0].rule_id)
        assert 0.0 <= metrics.quality_score <= 100.0


def test_quality_analyzer_with_feedback():
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    feedback = FeedbackManager()
    rules = repo.list_rules(enabled_only=True)
    if rules:
        rule_id = rules[0].rule_id
        feedback.add(
            FeedbackEntry(
                conversation_id="c1",
                question="?",
                reasoning_trace={},
                rules_used=[rule_id],
                response=".",
                rating="Very Helpful",
            )
        )
        analyzer = QualityAnalyzer(repo, feedback)
        metrics = analyzer.analyze(rule_id)
        assert metrics.positive_feedback == 1
