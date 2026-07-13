"""Feedback service."""

from sqlalchemy.orm import Session

from divyadrishti.models import Feedback
from divyadrishti.repositories import FeedbackRepository


class FeedbackService:
    """Business logic for user feedback."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FeedbackRepository(db)

    def create(self, user_id: int, data: dict) -> Feedback:
        mapped = {
            "conversation_id": data.get("conversation_id"),
            "message_id": data.get("message_id"),
            "rating": data.get("rating"),
            "comment": data.get("comment"),
            "response_text": data.get("response_text"),
            "reasoning_trace_json": data.get("reasoning_trace"),
            "rules_used_json": data.get("rules_used"),
        }
        feedback = Feedback(user_id=user_id, **mapped)
        return self.repo.create(feedback)

    def list_by_user(self, user_id: int) -> list[Feedback]:
        return self.repo.list_by_user(user_id)
