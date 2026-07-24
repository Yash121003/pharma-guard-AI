"""
Phase 3 smoke test: inserts real rows through the ORM to verify models,
relationships, enums, and constraints all work against the live Postgres
database. Run manually with:

    python -m tests.smoke_test_models

This is a throwaway verification script, not a pytest suite (that comes
in Phase 9 - Testing).
"""
from datetime import date, datetime, UTC

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.ai_conversation import AIConversation, MessageRole
from app.models.batch import Batch
from app.models.complaint import (
    Complaint,
    ComplaintSource,
    ComplaintStatus,
    ComplaintType,
    PriorityLevel,
    SeverityLevel,
)
from app.models.product import Product
from app.models.user import User, UserRole


def run() -> None:
    db = SessionLocal()
    try:
        # Clean slate for repeatable runs
        from app.models.audit_log import AuditLog

        db.query(AIConversation).delete()
        db.query(AuditLog).delete()  # FK references users; must clear before deleting users
        db.query(Complaint).delete()
        db.query(Batch).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()

        user = User(
            email="qa.manager@pharmaco.test",
            hashed_password=hash_password("Str0ngPassword!"),
            full_name="Asha Verma",
            role=UserRole.QA_MANAGER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
        print(f"[OK] Created {user}")

        product = Product(name="Paracetamol", strength_grade="500mg")
        db.add(product)
        db.commit()
        db.refresh(product)
        print(f"[OK] Created {product}")

        batch = Batch(
            batch_number="PCM-2026-0417",
            product_id=product.id,
            manufacturing_date=date(2026, 1, 10),
            expiry_date=date(2028, 1, 10),
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        print(f"[OK] Created {batch}")

        complaint = Complaint(
            complaint_source=ComplaintSource.EMAIL,
            customer_name="MedPlus Pharmacy",
            product_id=product.id,
            product_name_raw="Paracetamol 500mg Tablets",
            strength="500mg",
            batch_id=batch.id,
            batch_number_raw="PCM-2026-0417",
            manufacturing_date=batch.manufacturing_date,
            expiry_date=batch.expiry_date,
            quantity_affected=12.5,
            quantity_unit="kg",
            complaint_type=ComplaintType.PACKAGING_DEFECT,
            complaint_date=date(2026, 7, 20),
            description="Blister packaging seal was broken on 3 strips within the received carton.",
            initial_severity=SeverityLevel.MEDIUM,
            priority=PriorityLevel.HIGH,
            status=ComplaintStatus.PENDING_TRIAGE,
            created_by_id=user.id,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        print(f"[OK] Created {complaint}")

        convo = AIConversation(
            complaint_id=complaint.id,
            role=MessageRole.ASSISTANT,
            message="I've extracted the complaint details from the uploaded PDF and populated the form.",
            tool_used="extract",
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)
        print(f"[OK] Created {convo}")

        # Verify relationships resolve correctly
        fetched = db.query(Complaint).filter_by(id=complaint.id).one()
        assert fetched.product.name == "Paracetamol"
        assert fetched.batch.batch_number == "PCM-2026-0417"
        assert fetched.created_by.email == "qa.manager@pharmaco.test"
        assert len(fetched.conversations) == 1
        assert fetched.conversations[0].role == MessageRole.ASSISTANT
        print("[OK] All relationships resolved correctly")

        print(f"\nSmoke test passed at {datetime.now(UTC).isoformat()}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
