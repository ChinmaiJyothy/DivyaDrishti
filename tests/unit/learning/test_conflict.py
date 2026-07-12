from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import ConflictAnalyzer


def test_conflict_analyzer():
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    analyzer = ConflictAnalyzer(repo)

    duplicates = analyzer.find_duplicates()
    conflicts = analyzer.find_conflicts()

    assert isinstance(duplicates, list)
    assert isinstance(conflicts, list)
