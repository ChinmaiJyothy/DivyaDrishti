from divyadrishti.knowledge import Rule, TrainingDatasetExporter
from divyadrishti.knowledge.models import AstrologicalFactors


def test_export_training_entry(tmp_path):
    rule = Rule(
        rule_id="BPHS_7TH_001",
        source_book="BPHS",
        topic="Marriage",
        category="marriage",
        conditions=["Jupiter aspects the 7th house"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
        interpretation="Happy marriage.",
        confidence=0.8,
    )

    exporter = TrainingDatasetExporter()
    entry = exporter.build_from_rule(
        rule=rule,
        chart={"lagna": "Aries"},
        question="Will I have a happy marriage?",
        final_answer="Yes, a harmonious marriage is indicated.",
    )

    output = tmp_path / "dataset.jsonl"
    exporter.export([entry], output)

    assert output.exists()
    assert entry.birth_chart["lagna"] == "Aries"
    assert entry.source_references[0]["rule_id"] == "BPHS_7TH_001"
