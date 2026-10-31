"""
SQLAlchemy 2.0 models for Quotations and Quotation Lines.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Quotation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "quotations"

    quotation_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", index=True, nullable=False)
    
    # Financial summary fields (stored as NUMERIC(12, 2) in INR)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    lines: Mapped[List["QuotationLine"]] = relationship(
        "QuotationLine",
        back_populates="quotation",
        cascade="all, delete-orphan",
        order_by="QuotationLine.created_at",
    )
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        back_populates="quotation",
        uselist=False,
    )


class QuotationLine(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "quotation_lines"

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quotations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True, nullable=True)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True, nullable=True)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    # Frozen snapshot fields
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_rate_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="lines")

