import pytest

from divyadrishti.knowledge import AstrologicalFactors, Book, Citation, Rule, TrainingEntry
from divyadrishti.knowledge.exceptions import RuleValidationError
from divyadrishti.knowledge.validation import RuleValidator


def test_rule_creation():
    rule = Rule(
        rule_id="BPHS_7TH_001",
        source_book="BPHS",
        chapter="16",
        verse="1",
        topic="Marriage",
        category="marriage",
        conditions=["Jupiter is strong in the 7th house"],
        astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
        interpretation="Harmonious marriage.",
        confidence=0.85,
    )
    assert rule.rule_id == "BPHS_7TH_001"
    assert rule.astrological_factors.houses == [7]
    assert rule.citation().source_book == "BPHS"


def test_book_creation():
    book = Book(
        book_id="BPHS",
        title="Brihat Parashara Hora Shastra",
        chapters={"7": "Houses"},
    )
    assert book.book_id == "BPHS"
    assert book.title.startswith("Brihat")


def test_citation_model():
    citation = Citation(
        rule_id="BPHS_7TH_001",
        source_book="BPHS",
        chapter="16",
        verse="1",
    )
    assert citation.verse == "1"


def test_training_entry():
    entry = TrainingEntry(
        birth_chart={"lagna": "Aries"},
        question="Will I marry?",
        relevant_rules=[],
        reasoning_steps=["Step 1"],
        final_answer="Yes, after a delay.",
        source_references=[],
    )
    assert entry.question == "Will I marry?"


def test_invalid_house_in_validation():
    data = {
        "rule_id": "BPHS_TEST_001",
        "source_book": "BPHS",
        "topic": "Test",
        "category": "marriage",
        "conditions": ["Test"],
        "astrological_factors": {"houses": [13]},
        "interpretation": "Test.",
        "confidence": 0.5,
    }
    validator = RuleValidator()
    with pytest.raises(RuleValidationError, match="Invalid house number"):
        validator.validate(data)


def test_invalid_planet():
    data = {
        "rule_id": "BPHS_TEST_002",
        "source_book": "BPHS",
        "topic": "Test",
        "category": "marriage",
        "conditions": ["Test"],
        "astrological_factors": {"planets": ["Pluto"]},
        "interpretation": "Test.",
        "confidence": 0.5,
    }
    validator = RuleValidator()
    with pytest.raises(RuleValidationError, match="Invalid planet"):
        validator.validate(data)
