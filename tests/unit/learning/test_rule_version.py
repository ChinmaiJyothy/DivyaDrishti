import pytest
from pathlib import Path

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.models import AstrologicalFactors, Rule
from divyadrishti.learning import RuleVersionManager


@pytest.fixture
def repository(tmp_path):
    repo = KnowledgeRepository(tmp_path)
    repo.add_rule(
        Rule(
            rule_id="BPHS_7TH_001",
            source_book="BPHS",
            topic="Marriage",
            category="marriage",
            conditions=["Jupiter in 7th"],
            astrological_factors=AstrologicalFactors(houses=[7], planets=["Jupiter"]),
            interpretation="Happy marriage.",
            confidence=0.8,
        ),
        save=False,
    )
    return repo


def test_propose_and_approve_rule(repository):
    manager = RuleVersionManager(repository)
    rule = Rule(
        rule_id="NEW_001",
        source_book="BPHS",
        topic="Career",
        category="career",
        conditions=["Sun in 10th"],
        astrological_factors=AstrologicalFactors(houses=[10], planets=["Sun"]),
        interpretation="Success in career.",
        confidence=0.7,
    )
    manager.propose_rule(rule)
    assert len(manager.pending_rules) == 1

    approved = manager.approve_rule("NEW_001")
    assert approved.approval_status == "approved"
    assert approved.enabled is True
    assert repository.get_rule("NEW_001") is not None


def test_deprecate_rule(repository):
    manager = RuleVersionManager(repository)
    deprecated = manager.deprecate_rule("BPHS_7TH_001")
    assert deprecated.deprecated is True
    assert deprecated.enabled is False


def test_update_rule_increments_version(repository):
    manager = RuleVersionManager(repository)
    rule = repository.get_rule("BPHS_7TH_001")
    rule.interpretation = "Very happy marriage."
    updated = manager.update_rule(rule)
    assert updated.version != "1.0.0"
    assert updated.change_history[-1]["action"] == "updated"
