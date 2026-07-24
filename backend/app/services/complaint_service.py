"""
Complaint business logic: creating a complaint from the intake form,
resolving/creating the linked Product and Batch records so the data stays
normalized even though the AI extracts free-text product/batch names.
"""
from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.complaint import Complaint
from app.models.product import Product
from app.schemas.complaint import ComplaintCreate
from app.utils.exceptions import NotFoundError


def _resolve_product(db: Session, product_name: str | None, strength: str | None) -> Product | None:
    if not product_name:
        return None
    product = db.query(Product).filter(Product.name == product_name).first()
    if product is None:
        product = Product(name=product_name, strength_grade=strength)
        db.add(product)
        db.flush()  # get product.id without committing yet
    return product


def _resolve_batch(
    db: Session, product: Product | None, batch_number: str | None, mfg_date, exp_date
) -> Batch | None:
    if not batch_number or product is None:
        return None
    batch = (
        db.query(Batch).filter(Batch.batch_number == batch_number, Batch.product_id == product.id).first()
    )
    if batch is None:
        batch = Batch(
            batch_number=batch_number,
            product_id=product.id,
            manufacturing_date=mfg_date,
            expiry_date=exp_date,
        )
        db.add(batch)
        db.flush()
    return batch


def create_complaint(db: Session, payload: ComplaintCreate, created_by_id: int | None) -> Complaint:
    product = _resolve_product(db, payload.product_name, payload.strength)
    batch = _resolve_batch(db, product, payload.batch_number, payload.manufacturing_date, payload.expiry_date)

    complaint = Complaint(
        complaint_source=payload.complaint_source,
        customer_name=payload.customer_name,
        product_id=product.id if product else None,
        product_name_raw=payload.product_name,
        strength=payload.strength,
        batch_id=batch.id if batch else None,
        batch_number_raw=payload.batch_number,
        manufacturing_date=payload.manufacturing_date,
        expiry_date=payload.expiry_date,
        quantity_affected=payload.quantity_affected,
        quantity_unit=payload.quantity_unit,
        complaint_type=payload.complaint_type,
        complaint_date=payload.complaint_date,
        description=payload.description,
        initial_severity=payload.initial_severity,
        priority=payload.priority,
        source_document_path=payload.source_document_path,
        source_document_type=payload.source_document_type,
        created_by_id=created_by_id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint_or_404(db: Session, complaint_id: int) -> Complaint:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise NotFoundError(f"Complaint {complaint_id} not found.")
    return complaint


def complaint_to_ai_dict(complaint: Complaint) -> dict:
    """Flattens a Complaint ORM object into the plain dict shape the AI
    graph nodes expect (product_name / batch_number instead of the raw/FK
    split used in the DB)."""
    return {
        "complaint_source": complaint.complaint_source.value,
        "customer_name": complaint.customer_name,
        "product_name": complaint.product.name if complaint.product else complaint.product_name_raw,
        "strength": complaint.strength,
        "batch_number": complaint.batch.batch_number if complaint.batch else complaint.batch_number_raw,
        "manufacturing_date": str(complaint.manufacturing_date) if complaint.manufacturing_date else None,
        "expiry_date": str(complaint.expiry_date) if complaint.expiry_date else None,
        "quantity_affected": float(complaint.quantity_affected) if complaint.quantity_affected else None,
        "complaint_type": complaint.complaint_type.value,
        "complaint_date": str(complaint.complaint_date),
        "description": complaint.description,
        "initial_severity": complaint.initial_severity.value,
        "priority": complaint.priority.value,
    }
