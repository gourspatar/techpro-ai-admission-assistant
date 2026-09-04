from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    conversation_id: int = Field(gt=0)
    role: str = Field(min_length=1, max_length=20)
    content: str = Field(min_length=1)


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    page: int
    limit: int
    total: int
    pages: int