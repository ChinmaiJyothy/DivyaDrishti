"""Conversation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationUpdateRequest,
    MessageCreateRequest,
    MessageResponse,
)
from divyadrishti.security import get_current_user
from divyadrishti.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _service(db: Session) -> ConversationService:
    return ConversationService(db)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    body: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _service(db).create(current_user.id, body.model_dump())


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    q: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _service(db).list(current_user.id, q)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = _service(db).get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    body: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return service.update(conversation, body.model_dump(exclude_unset=True))


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def add_message(
    conversation_id: int,
    body: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    return service.add_message(
        conversation_id,
        current_user.id,
        body.role,
        body.content,
        body.ai_response_json,
    )


@router.get("/{conversation_id}/messages/{message_id}", response_model=MessageResponse)
def get_message(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    for message in conversation.messages:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@router.post("/{conversation_id}/archive")
def archive_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.archive(conversation)
    return {"detail": "Conversation archived"}


@router.post("/{conversation_id}/resume")
def resume_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.resume(conversation)
    return {"detail": "Conversation resumed"}


@router.post("/{conversation_id}/pin")
def pin_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.update(conversation, {"is_pinned": True})
    return {"detail": "Conversation pinned"}


@router.post("/{conversation_id}/unpin")
def unpin_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.update(conversation, {"is_pinned": False})
    return {"detail": "Conversation unpinned"}


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.delete(conversation)
    return {"detail": "Conversation deleted"}


@router.delete("/{conversation_id}/messages/{message_id}")
def delete_message(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    service.delete_messages_from(conversation_id, message_id, current_user.id)
    return {"detail": "Messages deleted"}


@router.get("/{conversation_id}/export")
def export_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _service(db)
    conversation = service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return service.export(conversation)
