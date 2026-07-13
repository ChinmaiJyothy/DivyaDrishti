"""Chat API routes for streaming AI conversations."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from divyadrishti.database import get_db
from divyadrishti.models import User
from divyadrishti.schemas.chat import ChatRequest
from divyadrishti.security import get_current_user
from divyadrishti.services.chat_service import ChatService
from divyadrishti.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])


def _knowledge_repository(request: Request):
    repo = getattr(request.app.state, "knowledge_repository", None)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge repository is not available.",
        )
    return repo


@router.post("/{conversation_id}")
def chat_stream(
    conversation_id: int,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    knowledge_repository=Depends(_knowledge_repository),
):
    """Stream an assistant response for a conversation as a Server-Sent Event stream."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    chat_service = ChatService(db, knowledge_repository)

    def event_generator():
        for event in chat_service.stream(conversation, body):
            yield f"data: {json.dumps(event)}\n\n".encode("utf-8")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
