from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseListResponse, CourseResponse, CourseUpdate


router = APIRouter(
    prefix="/api/v1/courses",
    tags=["Courses"],
)

@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
):
    existing_course = db.scalar(
        select(Course).where(Course.slug == course_data.slug)
    )

    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this slug already exists",
        )

    course = Course(**course_data.model_dump())

    db.add(course)
    db.commit()
    db.refresh(course)

    return course

@router.get(
    "",
    response_model=CourseListResponse,
)
def get_courses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
    level: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Course)

    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            Course.name.ilike(search_term)
            | Course.description.ilike(search_term)
        )

    if level:
        query = query.where(Course.level == level)

    if is_active is not None:
        query = query.where(Course.is_active == is_active)

    count_query = select(func.count()).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    offset = (page - 1) * limit

    courses = db.scalars(
        query
        .order_by(Course.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    pages = ceil(total / limit) if total else 0

    return CourseListResponse(
        items=courses,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

@router.get(
    "/{course_id}",
    response_model=CourseResponse,
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course

@router.put(
    "/{course_id}",
    response_model=CourseResponse,
)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
):
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    update_data = course_data.model_dump(exclude_unset=True)

    if "slug" in update_data:
        existing_course = db.scalar(
            select(Course).where(
                Course.slug == update_data["slug"],
                Course.id != course_id,
            )
        )

        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A course with this slug already exists",
            )

    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return course

@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    db.delete(course)
    db.commit()