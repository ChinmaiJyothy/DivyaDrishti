"""Tests for CorpusService book ingestion and automatic candidate rule creation."""

import pytest

from divyadrishti.models import (
    CandidateRule,
    CandidateRuleStatus,
    Corpus,
    Role,
    UploadedBook,
    User,
)
from divyadrishti.services.corpus_service import CorpusService


@pytest.fixture
def service(db):
    return CorpusService(db)


@pytest.fixture
def sample_book(db, tmp_path):
    role = Role(name="admin")
    user = User(email="admin@example.com", name="Admin", hashed_password="x", role=role)
    corpus = Corpus(slug="test-corpus", name="Test Corpus")
    db.add_all([role, user, corpus])
    db.flush()

    book_file = tmp_path / "test_book.txt"
    book_file.write_text(
        "# Chapter 1\n\nVerse 1: Jupiter in the 7th house gives a happy marriage.\n\n"
        "Verse 2: Saturn in the 7th house delays marriage.\n"
    )

    book = UploadedBook(
        user_id=user.id,
        corpus_id=corpus.id,
        file_path=str(book_file),
        file_name="test_book.txt",
        title="Test Book",
        author="Tester",
        language="en",
    )
    db.add(book)
    db.commit()
    return book


def test_ingest_book_creates_candidate_rules_and_leaves_pending(
    db, service, sample_book
):
    report = service.ingest_book(sample_book.id)

    assert report.stored_pages == 1
    assert report.candidate_rule_count >= 1
    assert report.errors == []

    candidates = (
        db.query(CandidateRule)
        .filter(CandidateRule.book_id == sample_book.id)
        .all()
    )
    assert len(candidates) == report.candidate_rule_count
    assert all(c.status == CandidateRuleStatus.PENDING.value for c in candidates)

    rule = next(c for c in candidates if "Jupiter" in c.original_text or "Saturn" in c.original_text)
    assert rule.corpus_id == sample_book.corpus_id
    assert rule.topic == "marriage"
    assert 7 in rule.astrological_factors_json.get("houses", [])
    assert "Jupiter" in rule.astrological_factors_json.get("planets", []) or "Saturn" in rule.astrological_factors_json.get("planets", [])
    assert 0.0 < rule.confidence <= 1.0
