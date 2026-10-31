"""
SQLAlchemy 2.0 models for Subscriptions and Subscription Lines.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Subscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    subscription_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    
    # One quotation can convert to at most one subscription (Idempotency guarantee)
    quotation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("quotations.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True, nullable=False)
    billing_frequency: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    # Recurring totals
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    # Lifecycle dates
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_billing_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    quotation: Mapped[Optional["Quotation"]] = relationship("Quotation", back_populates="subscription")
    lines: Mapped[List["SubscriptionLine"]] = relationship(
        "SubscriptionLine",
        back_populates="subscription",
        cascade="all, delete-orphan",
        order_by="SubscriptionLine.created_at",
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice",
        back_populates="subscription",
        order_by="Invoice.billing_period_start.desc()",
    )


class SubscriptionLine(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscription_lines"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True, nullable=True)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    # Line item snapshots
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_rate_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="lines")

