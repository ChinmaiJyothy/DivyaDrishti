"""Knowledge version repository."""

from sqlalchemy.orm import Session

from divyadrishti.models import KnowledgeVersion


class KnowledgeVersionRepository:
    """Database operations for knowledge rule versions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[KnowledgeVersion]:
        return (
            self.db.query(KnowledgeVersion)
            .order_by(KnowledgeVersion.created_at.desc())
            .all()
        )

    def get_latest(self) -> KnowledgeVersion | None:
        return (
            self.db.query(KnowledgeVersion)
            .order_by(KnowledgeVersion.modified_at.desc())
            .first()
        )
