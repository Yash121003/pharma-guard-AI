"""
Pydantic schemas for the Complaint resource -- request/response shapes
for the create/save, list, and detail endpoints.
"""
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.complaint import ComplaintSource, ComplaintStatus, ComplaintType, PriorityLevel, SeverityLevel


class ComplaintCreate(BaseModel):
    """Matches the 'Save Complaint' form submission -- the AI-populated
    (and possibly user-edited) fields from the intake form."""

    complaint_source: ComplaintSource
    customer_name: str = Field(min_length=1, max_length=255)

    product_name: str | None = Field(default=None, max_length=255)
    strength: str | None = Field(default=None, max_length=100)
    batch_number: str | None = Field(default=None, max_length=100)
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    quantity_affected: float | None = None
    quantity_unit: str | None = Field(default="kg", max_length=20)

    complaint_type: ComplaintType
    complaint_date: date
    description: str = Field(min_length=1)

    initial_severity: SeverityLevel
    priority: PriorityLevel

    source_document_path: str | None = None
    source_document_type: str | None = None


class ComplaintPublic(BaseModel):
    id: int
    complaint_source: ComplaintSource
    customer_name: str
    product_id: int | None
    product_name_raw: str | None
    strength: str | None
    batch_id: int | None
    batch_number_raw: str | None
    manufacturing_date: date | None
    expiry_date: date | None
    quantity_affected: float | None
    quantity_unit: str | None
    complaint_type: ComplaintType
    complaint_date: date
    description: str
    initial_severity: SeverityLevel
    priority: PriorityLevel
    status: ComplaintStatus
    ai_summary: str | None
    ai_root_cause: str | None
    ai_capa_recommendation: str | None
    ai_risk_level: str | None
    ai_completeness_score: float | None
    ai_completeness_notes: str | None
    is_duplicate_of_id: int | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplaintListItem(BaseModel):
    id: int
    customer_name: str
    product_name_raw: str | None
    complaint_type: ComplaintType
    status: ComplaintStatus
    priority: PriorityLevel
    complaint_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
