"""Feedback repository."""

from sqlalchemy.orm import Session

from divyadrishti.models import Feedback


class FeedbackRepository:
    """Database operations for feedback."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def list_by_user(self, user_id: int) -> list[Feedback]:
        return self.db.query(Feedback).filter(Feedback.user_id == user_id).all()
