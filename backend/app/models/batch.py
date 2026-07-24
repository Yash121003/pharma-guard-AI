"""
Batch model -- manufacturing batch/lot tracking, linked to a Product.
"""
from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Batch(Base, TimestampMixin):
    __tablename__ = "batches"
    __table_args__ = (UniqueConstraint("batch_number", "product_id", name="uq_batch_number_product"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    product: Mapped["Product"] = relationship(back_populates="batches")  # noqa: F821
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="batch")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Batch id={self.id} batch_number={self.batch_number!r} product_id={self.product_id}>"
