from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class CourseBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=10)
    level: str = Field(min_length=2, max_length=50)
    duration_weeks: int = Field(gt=0)
    fee: int = Field(ge=0)
    is_active: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, min_length=10)
    level: str | None = Field(default=None, min_length=2, max_length=50)
    duration_weeks: int | None = Field(default=None, gt=0)
    fee: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    page: int
    limit: int
    total: int
    pages: int