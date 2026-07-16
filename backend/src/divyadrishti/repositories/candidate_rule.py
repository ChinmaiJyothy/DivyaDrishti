"""Candidate rule and review audit repositories."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from divyadrishti.models import CandidateRule, CandidateRuleStatus, RuleReviewAudit


class CandidateRuleRepository:
    """Database operations for candidate rules extracted from corpus books."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, candidate: CandidateRule) -> CandidateRule:
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def bulk_create(self, candidates: list[CandidateRule]) -> list[CandidateRule]:
        self.db.add_all(candidates)
        self.db.commit()
        for candidate in candidates:
            self.db.refresh(candidate)
        return candidates

    def get_by_id(self, candidate_id: int) -> CandidateRule | None:
        return self.db.query(CandidateRule).filter(CandidateRule.id == candidate_id).first()

    def get_by_candidate_rule_id(self, candidate_rule_id: str) -> CandidateRule | None:
        return (
            self.db.query(CandidateRule)
            .filter(CandidateRule.candidate_rule_id == candidate_rule_id)
            .first()
        )

    def list(
        self,
        corpus_id: int | None = None,
        book_id: int | None = None,
        status: str | None = None,
        topic: str | None = None,
    ) -> list[CandidateRule]:
        query = self.db.query(CandidateRule)
        if corpus_id is not None:
            query = query.filter(CandidateRule.corpus_id == corpus_id)
        if book_id is not None:
            query = query.filter(CandidateRule.book_id == book_id)
        if status is not None:
            query = query.filter(CandidateRule.status == status)
        if topic is not None:
            query = query.filter(CandidateRule.topic == topic)
        return query.order_by(CandidateRule.created_at.desc()).all()

    def list_approved_for_corpora(self, corpus_ids: list[int]) -> list[CandidateRule]:
        if not corpus_ids:
            return []
        return (
            self.db.query(CandidateRule)
            .filter(
                CandidateRule.corpus_id.in_(corpus_ids),
                CandidateRule.status == CandidateRuleStatus.APPROVED.value,
            )
            .all()
        )

    def update(self, candidate: CandidateRule) -> CandidateRule:
        candidate.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate


class RuleReviewAuditRepository:
    """Database operations for the rule review audit trail."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, entry: RuleReviewAudit) -> RuleReviewAudit:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_for_candidate(self, candidate_rule_id: int) -> list[RuleReviewAudit]:
        return (
            self.db.query(RuleReviewAudit)
            .filter(RuleReviewAudit.candidate_rule_id == candidate_rule_id)
            .order_by(RuleReviewAudit.created_at.asc())
            .all()
        )
