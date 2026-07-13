"""Conversation service."""

from sqlalchemy.orm import Session

from divyadrishti.models import Conversation, Message
from divyadrishti.repositories import ConversationRepository


class ConversationService:
    """Business logic for conversations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ConversationRepository(db)

    def list(self, user_id: int, q: str | None = None) -> list[Conversation]:
        return self.repo.list_by_user(user_id, q)

    def get(self, conversation_id: int, user_id: int) -> Conversation | None:
        return self.repo.get_by_id(conversation_id, user_id)

    def create(self, user_id: int, data: dict) -> Conversation:
        conversation = Conversation(user_id=user_id, **data)
        return self.repo.create(conversation)

    def update(self, conversation: Conversation, data: dict) -> Conversation:
        allowed = {"title", "birth_profile_id", "is_archived", "is_pinned"}
        for key, value in data.items():
            if key in allowed and value is not None:
                setattr(conversation, key, value)
        return self.repo.update(conversation)

    def get_message(self, message_id: int, user_id: int) -> Message | None:
        return self.repo.get_message(message_id, user_id)

    def delete_messages_after(self, conversation_id: int, message_id: int, user_id: int) -> int:
        conversation = self.get(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")
        return self.repo.delete_messages_after(conversation_id, message_id)

    def delete_messages_from(self, conversation_id: int, message_id: int, user_id: int) -> int:
        conversation = self.get(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")
        return self.repo.delete_messages_from(conversation_id, message_id)

    def add_message(
        self,
        conversation_id: int,
        user_id: int,
        role: str,
        content: str,
        ai_response: dict | None = None,
    ) -> Message:
        conversation = self.get(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            ai_response_json=ai_response,
        )
        return self.repo.add_message(message)

    def archive(self, conversation: Conversation) -> Conversation:
        conversation.is_archived = True
        return self.repo.update(conversation)

    def resume(self, conversation: Conversation) -> Conversation:
        conversation.is_archived = False
        return self.repo.update(conversation)

    def delete(self, conversation: Conversation) -> Conversation:
        return self.repo.soft_delete(conversation)

    def export(self, conversation: Conversation) -> dict:
        return {
            "id": conversation.id,
            "title": conversation.title,
            "domain": conversation.domain,
            "messages": [
                {"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()}
                for msg in conversation.messages
            ],
        }
