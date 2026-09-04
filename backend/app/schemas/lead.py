from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    course_interest: str | None = Field(default=None, max_length=150)
    message: str | None = None
    status: str = Field(default="new", max_length=30)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    course_interest: str | None = Field(default=None, max_length=150)
    message: str | None = None
    status: str | None = Field(default=None, max_length=30)


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    page: int
    limit: int
    total: int
    pages: int