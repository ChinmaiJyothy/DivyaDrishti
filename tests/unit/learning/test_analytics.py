from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import KnowledgeAnalytics


def test_knowledge_analytics():
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    analytics = KnowledgeAnalytics(repo)

    coverage = analytics.knowledge_coverage()
    assert "total_rules" in coverage
    assert "unique_topics" in coverage

    most_used = analytics.most_used_books()
    assert isinstance(most_used, list)

    unused = analytics.unused_rules()
    assert isinstance(unused, list)
