"""
SQLAlchemy 2.0 model for Payments.
Tracks payment attempts, references, and reconciliation against Invoices.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    payment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="simulation", nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), default="SUCCESS", index=True, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")

