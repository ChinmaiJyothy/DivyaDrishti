import pytest

from divyadrishti.knowledge import (
    KnowledgeRepository,
    KnowledgeRetrievalEngine,
    Rule,
    RuleValidator,
)


@pytest.fixture
def repo(tmp_path):
    kb = tmp_path / "knowledge-base"
    rules_dir = kb / "rules" / "marriage"
    rules_dir.mkdir(parents=True)
    rules_file = rules_dir / "rules.yaml"
    rules_file.write_text(
        """
- rule_id: BPHS_7TH_001
  source_book: BPHS
  topic: Marriage
  category: marriage
  conditions:
    - Jupiter aspects the 7th house
  astrological_factors:
    houses: [7]
    planets: [Jupiter]
  interpretation: Happy marriage.
  confidence: 0.8

- rule_id: BPHS_7TH_002
  source_book: BPHS
  topic: Marriage
  category: marriage
  conditions:
    - Saturn aspects the 7th house
  astrological_factors:
    houses: [7]
    planets: [Saturn]
  interpretation: Delayed marriage.
  confidence: 0.7
""",
        encoding="utf-8",
    )
    repository = KnowledgeRepository(kb)
    repository.load()
    return repository


def test_retrieve_by_house(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_house(7)
    assert len(rules) == 2


def test_retrieve_by_planet(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_planet("Jupiter")
    assert len(rules) == 1
    assert rules[0].rule_id == "BPHS_7TH_001"


def test_retrieve_by_combination(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_combination({"houses": [7], "planets": ["Jupiter"]})
    assert len(rules) >= 1
    assert rules[0].rule_id == "BPHS_7TH_001"


def test_retrieve_by_query(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_query("Saturn")
    assert len(rules) == 1
    assert rules[0].rule_id == "BPHS_7TH_002"


def test_retrieve_by_topic(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_topic("Marriage")
    assert len(rules) == 2


def test_retrieve_by_source(repo):
    engine = KnowledgeRetrievalEngine(repo)
    rules = engine.retrieve_by_source("BPHS")
    assert len(rules) == 2
