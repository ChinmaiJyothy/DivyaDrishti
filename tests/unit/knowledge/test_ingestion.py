import pytest

from divyadrishti.knowledge import KnowledgeIngestionPipeline
from divyadrishti.knowledge.exceptions import IngestionError


def test_ingest_yaml(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
- rule_id: BPHS_TEST_001
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
""",
        encoding="utf-8",
    )

    pipeline = KnowledgeIngestionPipeline()
    rules = pipeline.ingest_file(rules_file)
    assert len(rules) == 1
    assert rules[0].rule_id == "BPHS_TEST_001"


def test_ingest_json(tmp_path):
    rules_file = tmp_path / "rules.json"
    rules_file.write_text(
        """
[
  {
    "rule_id": "BPHS_TEST_002",
    "source_book": "BPHS",
    "topic": "Career",
    "category": "career",
    "conditions": ["10th lord is strong"],
    "astrological_factors": {"houses": [10]},
    "interpretation": "Career success.",
    "confidence": 0.8
  }
]
""",
        encoding="utf-8",
    )

    pipeline = KnowledgeIngestionPipeline()
    rules = pipeline.ingest_file(rules_file)
    assert len(rules) == 1
    assert rules[0].topic == "Career"


def test_ingest_markdown(tmp_path):
    rules_file = tmp_path / "rule.md"
    rules_file.write_text(
        """---
rule_id: BPHS_TEST_003
source_book: BPHS
topic: Finance
category: finance
conditions:
  - Jupiter and Venus influence the 2nd house
astrological_factors:
  houses: [2]
  planets: [Jupiter, Venus]
confidence: 0.85
---
Wealth accumulation is supported when Jupiter and Venus influence the 2nd house.
""",
        encoding="utf-8",
    )

    pipeline = KnowledgeIngestionPipeline()
    rules = pipeline.ingest_file(rules_file)
    assert len(rules) == 1
    assert rules[0].interpretation.startswith("Wealth accumulation")


def test_ingest_invalid_file():
    pipeline = KnowledgeIngestionPipeline()
    with pytest.raises(IngestionError):
        pipeline.ingest_file("nonexistent.yaml")


def test_ingest_invalid_extension(tmp_path):
    bad_file = tmp_path / "rules.txt"
    bad_file.write_text("invalid", encoding="utf-8")
    pipeline = KnowledgeIngestionPipeline()
    with pytest.raises(IngestionError, match="Unsupported file format"):
        pipeline.ingest_file(bad_file)
