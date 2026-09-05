from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import (
    ChatMessage,
    SYSTEM_PROMPT,
    generate_ai_response,
)


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    # 1. Find the conversation
    conversation = db.get(
        Conversation,
        request.conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # 2. Save the user's message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # 3. Load conversation history
    result = db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc(), Message.id.asc())
    )

    messages = result.scalars().all()

    # 4. Build AI messages
    ai_messages: list[ChatMessage] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    for message in messages:
        ai_messages.append(
            {
                "role": message.role,
                "content": message.content,
            }
        )

    # 5. Generate AI response
    reply = generate_ai_response(ai_messages)

    # 6. Save AI response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # 7. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        reply=reply,
    )