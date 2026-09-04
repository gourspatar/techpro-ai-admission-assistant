from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationBase(BaseModel):
    lead_id: int = Field(gt=0)
    status: str = Field(default="active", max_length=30)


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=30)


class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    page: int
    limit: int
    total: int
    pages: int