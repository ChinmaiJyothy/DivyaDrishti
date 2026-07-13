"""Report repository."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from divyadrishti.models import Report


class ReportRepository:
    """Database operations for user reports."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user(self, user_id: int) -> list[Report]:
        return (
            self.db.query(Report)
            .filter(Report.user_id == user_id, Report.is_deleted.is_(False))
            .order_by(Report.created_at.desc())
            .all()
        )

    def get_by_id(self, report_id: int, user_id: int) -> Report | None:
        return (
            self.db.query(Report)
            .filter(
                Report.id == report_id,
                Report.user_id == user_id,
                Report.is_deleted.is_(False),
            )
            .first()
        )

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def update(self, report: Report) -> Report:
        report.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(report)
        return report

    def soft_delete(self, report: Report) -> Report:
        report.is_deleted = True
        report.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(report)
        return report
