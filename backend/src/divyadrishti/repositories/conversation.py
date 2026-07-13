"""Conversation repository."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from divyadrishti.models import Conversation, Message


class ConversationRepository:
    """Database operations for conversations and messages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user(self, user_id: int) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id, Conversation.is_deleted.is_(False))
            .options(selectinload(Conversation.messages).selectinload(Message.reasoning_results))
            .all()
        )

    def get_by_id(self, conversation_id: int, user_id: int) -> Conversation | None:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_deleted.is_(False),
            )
            .options(selectinload(Conversation.messages).selectinload(Message.reasoning_results))
            .first()
        )

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update(self, conversation: Conversation) -> Conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def soft_delete(self, conversation: Conversation) -> Conversation:
        conversation.is_deleted = True
        conversation.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def add_message(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
