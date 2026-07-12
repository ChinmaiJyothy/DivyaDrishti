import pytest

from divyadrishti.knowledge import DuplicateRuleError, RuleValidationError, RuleValidator


def test_valid_rule():
    data = {
        "rule_id": "BPHS_TEST_001",
        "source_book": "BPHS",
        "topic": "Marriage",
        "category": "marriage",
        "conditions": ["Jupiter aspects the 7th house"],
        "astrological_factors": {"houses": [7], "planets": ["Jupiter"]},
        "interpretation": "Happy marriage.",
        "confidence": 0.8,
    }
    validator = RuleValidator()
    rule = validator.validate(data)
    assert rule.rule_id == "BPHS_TEST_001"


def test_duplicate_rule_id():
    data = {
        "rule_id": "BPHS_TEST_001",
        "source_book": "BPHS",
        "topic": "Marriage",
        "category": "marriage",
        "conditions": ["Test"],
        "astrological_factors": {},
        "interpretation": "Test.",
        "confidence": 0.8,
    }
    validator = RuleValidator()
    with pytest.raises(DuplicateRuleError):
        validator.validate_batch([data, data])


def test_invalid_sign():
    data = {
        "rule_id": "BPHS_TEST_002",
        "source_book": "BPHS",
        "topic": "Test",
        "category": "marriage",
        "conditions": ["Test"],
        "astrological_factors": {"signs": ["Ophiuchus"]},
        "interpretation": "Test.",
        "confidence": 0.8,
    }
    validator = RuleValidator()
    with pytest.raises(RuleValidationError, match="Invalid sign"):
        validator.validate(data)


def test_invalid_confidence():
    data = {
        "rule_id": "BPHS_TEST_003",
        "source_book": "BPHS",
        "topic": "Test",
        "category": "marriage",
        "conditions": ["Test"],
        "astrological_factors": {},
        "interpretation": "Test.",
        "confidence": 1.5,
    }
    validator = RuleValidator()
    with pytest.raises(RuleValidationError):
        validator.validate(data)


def test_empty_conditions():
    data = {
        "rule_id": "BPHS_TEST_004",
        "source_book": "BPHS",
        "topic": "Test",
        "category": "marriage",
        "conditions": [],
        "astrological_factors": {},
        "interpretation": "Test.",
        "confidence": 0.8,
    }
    validator = RuleValidator()
    with pytest.raises(RuleValidationError, match="at least one condition"):
        validator.validate(data)
