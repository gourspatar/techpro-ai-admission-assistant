from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.lead import Lead
from app.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)


router = APIRouter(
    prefix="/api/v1/leads",
    tags=["Leads"],
)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
):
    lead = Lead(**lead_data.model_dump())

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


@router.get(
    "",
    response_model=LeadListResponse,
)
def get_leads(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
    status_filter: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Lead)

    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            Lead.name.ilike(search_term)
            | Lead.email.ilike(search_term)
            | Lead.phone.ilike(search_term)
            | Lead.course_interest.ilike(search_term)
        )

    if status_filter:
        query = query.where(Lead.status == status_filter)

    count_query = select(func.count()).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    offset = (page - 1) * limit

    leads = db.scalars(
        query
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    pages = ceil(total / limit) if total else 0

    return LeadListResponse(
        items=leads,
        page=page,
        limit=limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return lead


@router.put(
    "/{lead_id}",
    response_model=LeadResponse,
)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    update_data = lead_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    return lead


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    db.delete(lead)
    db.commit()