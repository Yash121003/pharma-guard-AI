"""
Complaint CRUD endpoints -- create (Save Complaint), list, and detail.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintListItem, ComplaintPublic
from app.services import complaint_service
from app.services.audit_service import log_action

router = APIRouter()


@router.post("", response_model=ComplaintPublic, status_code=201)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Complaint:
    complaint = complaint_service.create_complaint(db, payload, created_by_id=current_user.id)
    log_action(
        db, user_id=current_user.id, action="create", entity_type="complaint", entity_id=complaint.id
    )
    return complaint


@router.get("", response_model=list[ComplaintListItem])
def list_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Complaint]:
    return (
        db.query(Complaint)
        .order_by(desc(Complaint.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{complaint_id}", response_model=ComplaintPublic)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Complaint:
    return complaint_service.get_complaint_or_404(db, complaint_id)
