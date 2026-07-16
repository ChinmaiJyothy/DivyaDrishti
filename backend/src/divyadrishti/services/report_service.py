"""Report service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from divyadrishti.models import Report
from divyadrishti.repositories.report import ReportRepository


class ReportService:
    """Business logic for user reports."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReportRepository(db)

    def list(self, user_id: int) -> list[Report]:
        return self.repo.list_by_user(user_id)

    def get(self, report_id: int, user_id: int) -> Report | None:
        return self.repo.get_by_id(report_id, user_id)

    def create(self, user_id: int, data: dict) -> Report:
        report = Report(
            user_id=user_id,
            title=data["title"],
            category=data["category"],
            status="pending",
        )
        return self.repo.create(report)

    def update(self, report: Report, data: dict) -> Report:
        for key, value in data.items():
            if value is not None and hasattr(report, key):
                setattr(report, key, value)
        return self.repo.update(report)

    def delete(self, report: Report) -> Report:
        return self.repo.soft_delete(report)
