"""
Product model -- pharmaceutical product master data.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    strength_grade: Mapped[str | None] = mapped_column(String(100), nullable=True)

    batches: Mapped[list["Batch"]] = relationship(back_populates="product", cascade="all, delete-orphan")  # noqa: F821
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="product")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r}>"
