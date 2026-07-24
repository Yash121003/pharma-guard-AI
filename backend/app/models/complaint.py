"""
Complaint model -- the central entity of the QMS complaint module.

Field set matches the reference UI exactly (Origin & Customer Details,
Product & Batch Identification, Complaint Details, Initial Assessment &
Priority), plus AI-derived fields populated by the LangGraph workflow
(summary, root cause, CAPA, risk level, duplicate linkage).
"""
import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ComplaintSource(str, enum.Enum):
    PHONE = "phone"
    EMAIL = "email"
    PORTAL = "portal"
    LETTER = "letter"
    SALES_REP = "sales_rep"
    OTHER = "other"


class ComplaintType(str, enum.Enum):
    EFFICACY = "efficacy"
    PACKAGING_DEFECT = "packaging_defect"
    CONTAMINATION = "contamination"
    ADVERSE_EVENT = "adverse_event"
    LABELING_ERROR = "labeling_error"
    PHYSICAL_DEFECT = "physical_defect"
    OTHER = "other"


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ComplaintStatus(str, enum.Enum):
    PENDING_TRIAGE = "pending_triage"
    UNDER_INVESTIGATION = "under_investigation"
    CAPA_ASSIGNED = "capa_assigned"
    CLOSED = "closed"


class Complaint(Base, TimestampMixin):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)

    # --- 1. Origin & Customer Details ---
    complaint_source: Mapped[ComplaintSource] = mapped_column(
        Enum(ComplaintSource, name="complaint_source"), nullable=False
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- 2. Product & Batch Identification ---
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    product_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("batches.id"), nullable=True)
    batch_number_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity_affected: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(20), default="kg", nullable=True)

    # --- 3. Complaint Details ---
    complaint_type: Mapped[ComplaintType] = mapped_column(
        Enum(ComplaintType, name="complaint_type"), nullable=False
    )
    complaint_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # --- 4. Initial Assessment & Priority ---
    initial_severity: Mapped[SeverityLevel] = mapped_column(
        Enum(SeverityLevel, name="severity_level"), nullable=False
    )
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel, name="priority_level"), nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus, name="complaint_status"), default=ComplaintStatus.PENDING_TRIAGE, nullable=False
    )

    # --- Source document (uploaded PDF/DOCX/TXT/EML used for AI extraction) ---
    source_document_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_document_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- AI-derived fields (populated asynchronously by the LangGraph workflow) ---
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_capa_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ai_completeness_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ai_completeness_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_duplicate_of_id: Mapped[int | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)
    ai_last_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Ownership ---
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # --- Relationships ---
    product: Mapped["Product | None"] = relationship(back_populates="complaints")  # noqa: F821
    batch: Mapped["Batch | None"] = relationship(back_populates="complaints")  # noqa: F821
    created_by: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="complaints_created", foreign_keys=[created_by_id]
    )
    duplicate_of: Mapped["Complaint | None"] = relationship(remote_side=[id])
    conversations: Mapped[list["AIConversation"]] = relationship(  # noqa: F821
        back_populates="complaint", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Complaint id={self.id} customer={self.customer_name!r} status={self.status.value}>"
