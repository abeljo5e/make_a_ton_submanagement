import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Text, Numeric, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SubscriptionPlan(Base):
    """
    Subscription Plan Model (Member 2).
    Represents recurring pricing plans, billing intervals, policy flags, and availability.
    """
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    
    # Billing interval rules
    billing_interval: Mapped[str] = mapped_column(String(50), nullable=False, default="monthly")  # e.g., 'monthly', 'yearly', 'quarterly'
    billing_interval_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    minimum_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Availability windows
    available_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    available_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Policy / behavior flags
    auto_close: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_early_cancellation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_pause: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_renewal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    # Relationships
    plan_products: Mapped[List["PlanProduct"]] = relationship(
        "PlanProduct",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<SubscriptionPlan(id={self.id}, name='{self.name}', price={self.price}, billing_interval='{self.billing_interval}')>"


class PlanProduct(Base):
    """
    PlanProduct Association Model (Member 2).
    Represents product bundling inside subscription plans, including optional variants and quantities.
    """
    __tablename__ = "plan_products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Prevent duplicate plan-product-variant assignments in the same plan
    __table_args__ = (
        UniqueConstraint("plan_id", "product_id", "variant_id", name="uq_plan_product_variant"),
    )

    # Relationships
    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        back_populates="plan_products"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="plan_products"
    )
    variant: Mapped[Optional["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="plan_products"
    )

    def __repr__(self) -> str:
        return f"<PlanProduct(id={self.id}, plan_id={self.plan_id}, product_id={self.product_id}, variant_id={self.variant_id}, quantity={self.quantity})>"
