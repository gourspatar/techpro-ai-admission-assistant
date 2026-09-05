from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: int
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str