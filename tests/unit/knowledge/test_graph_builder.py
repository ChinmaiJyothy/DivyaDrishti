"""Tests for the KnowledgeGraphBuilder and traversal APIs."""

import pytest

from divyadrishti.knowledge.graph_builder import KnowledgeGraphBuilder
from divyadrishti.models import (
    CandidateRule,
    CandidateRuleStatus,
    Corpus,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    Role,
    UploadedBook,
    User,
)
from divyadrishti.repositories.knowledge_graph import KnowledgeGraphRepository


@pytest.fixture
def builder(db):
    repository = KnowledgeGraphRepository(db)
    return KnowledgeGraphBuilder(repository)


@pytest.fixture
def sample_data(db):
    role = Role(name="admin")
    user = User(email="test@example.com", name="Test", hashed_password="x", role=role)
    corpus = Corpus(slug="test-corpus", name="Test Corpus")
    db.add_all([role, user, corpus])
    db.flush()

    book = UploadedBook(
        user_id=user.id,
        corpus_id=corpus.id,
        file_path="/tmp/test.pdf",
        file_name="test.pdf",
        title="Test Book",
        author="Tester",
        language="en",
    )
    db.add(book)
    db.flush()

    rule = CandidateRule(
        candidate_rule_id="rule-1",
        corpus_id=corpus.id,
        book_id=book.id,
        source_book_title="Test Book",
        language="en",
        chapter="1",
        verse="5",
        page=12,
        original_text="Jupiter in 7th brings happiness.",
        candidate_interpretation="Jupiter in the 7th house gives a happy marriage.",
        topic="marriage",
        confidence=0.85,
        status=CandidateRuleStatus.APPROVED.value,
        astrological_factors_json={
            "planets": ["Jupiter"],
            "houses": [7],
            "signs": ["Libra"],
            "nakshatras": ["Swati"],
            "dashas": ["Jupiter"],
            "yogas": ["Gaja Kesari"],
            "doshas": ["Mangal"],
        },
    )
    db.add(rule)
    db.commit()
    return {"corpus": corpus, "book": book, "rule": rule}


def test_add_book_creates_book_node(builder, sample_data):
    book = sample_data["book"]
    corpus = sample_data["corpus"]

    book_node = builder.add_book(corpus.id, book)

    assert book_node.node_type == "book"
    assert book_node.ref_id == str(book.id)
    assert book_node.label == "Test Book"


def test_add_rule_creates_all_entity_nodes(builder, sample_data, db):
    corpus = sample_data["corpus"]
    book = sample_data["book"]
    rule = sample_data["rule"]

    builder.add_rule(corpus.id, book, rule)

    node_types = {n.node_type for n in db.query(KnowledgeGraphNode).all()}
    assert {
        "book",
        "chapter",
        "verse",
        "rule",
        "planet",
        "house",
        "sign",
        "nakshatra",
        "dasha",
        "yoga",
        "dosha",
    }.issubset(node_types)

    edge_count = db.query(KnowledgeGraphEdge).count()
    assert edge_count >= 10


def test_build_creates_graph_for_all_rules(builder, sample_data, db):
    corpus = sample_data["corpus"]
    book = sample_data["book"]
    rule = sample_data["rule"]

    rule_nodes = builder.build(corpus.id, book, [rule])

    assert len(rule_nodes) == 1
    assert rule_nodes[0].node_type == "rule"
    assert db.query(KnowledgeGraphNode).count() >= 11


def test_traverse_returns_subgraph(builder, sample_data):
    corpus = sample_data["corpus"]
    book = sample_data["book"]
    rule = sample_data["rule"]

    builder.build(corpus.id, book, [rule])
    subgraph = builder.traverse("planet", "Jupiter", depth=2, corpus_id=corpus.id)

    assert "nodes" in subgraph
    assert "edges" in subgraph
    node_types = {n["node_type"] for n in subgraph["nodes"]}
    assert "planet" in node_types
    assert "rule" in node_types


def test_find_rules_for_entity(builder, sample_data):
    corpus = sample_data["corpus"]
    book = sample_data["book"]
    rule = sample_data["rule"]

    builder.build(corpus.id, book, [rule])
    rules = builder.find_rules_for_entity(corpus.id, "planet", "Jupiter")

    assert len(rules) == 1
    assert rules[0]["node_type"] == "rule"


def test_find_related_entities(builder, sample_data):
    corpus = sample_data["corpus"]
    book = sample_data["book"]
    rule = sample_data["rule"]

    builder.build(corpus.id, book, [rule])
    entities = builder.find_related_entities(corpus.id, "rule-1")

    labels = {e["label"] for e in entities}
    assert "Jupiter" in labels
    assert "7" in labels
    assert "Libra" in labels
