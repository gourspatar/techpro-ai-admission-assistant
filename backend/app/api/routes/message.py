from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message import (
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)


router = APIRouter(
    prefix="/api/v1/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = db.get(
        Conversation,
        message_data.conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    message = Message(
        **message_data.model_dump()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get(
    "",
    response_model=MessageListResponse,
)
def get_messages(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    conversation_id: int | None = Query(default=None, gt=0),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Message)

    if conversation_id is not None:
        query = query.where(
            Message.conversation_id == conversation_id
        )

    if role:
        query = query.where(Message.role == role)

    count_query = select(func.count()).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    offset = (page - 1) * limit

    messages = db.scalars(
        query
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    pages = ceil(total / limit) if total else 0

    return MessageListResponse(
        items=messages,
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/{message_id}",
    response_model=MessageResponse,
)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
):
    message = db.get(Message, message_id)

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    return message


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
):
    message = db.get(Message, message_id)

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    db.delete(message)
    db.commit()