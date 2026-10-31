"""
Subscription Service implementing Phase 4 business logic:
- Subscription creation and line snapshots
- Lifecycle management (ACTIVE <-> PAUSED, ACTIVE -> CANCELED, EXPIRED)
- Allowed transition enforcement
- Renewal and billing date advancement
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.calculations import (
    calculate_line_amounts,
    calculate_next_billing_date,
    quantize_money,
)
from app.core.exceptions import (
    ConflictError,
    ExpiredError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.base import ensure_utc, utc_now
from app.models.subscription import Subscription, SubscriptionLine
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:
    @staticmethod
    def generate_subscription_number(db: Session) -> str:
        """Generate human-readable unique subscription number like SUB-202610-0001."""
        now = utc_now()
        prefix = f"SUB-{now.strftime('%Y%m')}-"
        count = db.scalar(select(func.count(Subscription.id)).where(Subscription.subscription_number.startswith(prefix))) or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    def create_subscription(db: Session, data: SubscriptionCreate) -> Subscription:
        """Create a direct subscription with line items."""
        if not data.lines:
            raise ValueError("Subscription must have at least one line item")

        # Check quotation_id uniqueness if provided
        if data.quotation_id:
            existing = db.scalar(select(Subscription).where(Subscription.quotation_id == data.quotation_id))
            if existing:
                raise ConflictError(f"Subscription already exists for quotation {data.quotation_id}")

        sub_number = SubscriptionService.generate_subscription_number(db)
        start_date = ensure_utc(data.start_date) or utc_now()
        next_billing_date = calculate_next_billing_date(start_date, data.billing_frequency)

        subscription = Subscription(
            subscription_number=sub_number,
            customer_id=data.customer_id,
            plan_id=data.plan_id,
            quotation_id=data.quotation_id,
            status="ACTIVE",
            billing_frequency=data.billing_frequency,
            currency=data.currency,
            start_date=start_date,
            next_billing_date=next_billing_date,
            end_date=ensure_utc(data.end_date),
            auto_renew=data.auto_renew,
            subtotal=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
        )

        subtotal = Decimal("0.00")
        discount_amount = Decimal("0.00")
        tax_amount = Decimal("0.00")
        total_amount = Decimal("0.00")

        for line_in in data.lines:
            calc = calculate_line_amounts(
                unit_price=line_in.unit_price,
                quantity=line_in.quantity,
                discount_pct=line_in.discount_pct,
                tax_rate_pct=line_in.tax_rate_pct,
            )
            line = SubscriptionLine(
                subscription=subscription,
                product_id=line_in.product_id,
                variant_id=line_in.variant_id,
                description=line_in.description,
                quantity=line_in.quantity,
                unit_price=calc.subtotal / Decimal(line_in.quantity),
                discount_pct=line_in.discount_pct,
                discount_amount=calc.discount_amount,
                tax_rate_pct=line_in.tax_rate_pct,
                tax_amount=calc.tax_amount,
                total_amount=calc.total_amount,
            )
            subscription.lines.append(line)
            subtotal += calc.subtotal
            discount_amount += calc.discount_amount
            tax_amount += calc.tax_amount
            total_amount += calc.total_amount

        subscription.subtotal = quantize_money(subtotal)
        subscription.discount_amount = quantize_money(discount_amount)
        subscription.tax_amount = quantize_money(tax_amount)
        subscription.total_amount = quantize_money(total_amount)

        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def get_subscription(db: Session, subscription_id: uuid.UUID) -> Optional[Subscription]:
        """Retrieve subscription by ID with eager loading."""
        stmt = (
            select(Subscription)
            .where(Subscription.id == subscription_id)
            .options(
                selectinload(Subscription.lines),
                selectinload(Subscription.invoices),
                selectinload(Subscription.quotation),
            )
        )
        return db.scalar(stmt)

    @staticmethod
    def list_subscriptions(
        db: Session,
        customer_id: Optional[uuid.UUID] = None,
        plan_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Subscription], int]:
        """List subscriptions with optional filters and pagination."""
        stmt = select(Subscription).options(selectinload(Subscription.lines)).order_by(Subscription.created_at.desc())
        count_stmt = select(func.count(Subscription.id))

        if customer_id:
            stmt = stmt.where(Subscription.customer_id == customer_id)
            count_stmt = count_stmt.where(Subscription.customer_id == customer_id)
        if plan_id:
            stmt = stmt.where(Subscription.plan_id == plan_id)
            count_stmt = count_stmt.where(Subscription.plan_id == plan_id)
        if status:
            stmt = stmt.where(Subscription.status == status.upper())
            count_stmt = count_stmt.where(Subscription.status == status.upper())

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total

    @staticmethod
    def pause_subscription(db: Session, subscription_id: uuid.UUID) -> Subscription:
        """Pause an ACTIVE subscription."""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {subscription_id} not found")
        if subscription.status != "ACTIVE":
            raise InvalidStateTransitionError(f"Cannot pause subscription in '{subscription.status}' status (must be ACTIVE)")

        subscription.status = "PAUSED"
        subscription.paused_at = utc_now()
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def resume_subscription(db: Session, subscription_id: uuid.UUID) -> Subscription:
        """Resume a PAUSED subscription and recalibrate billing schedule."""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {subscription_id} not found")
        if subscription.status != "PAUSED":
            raise InvalidStateTransitionError(f"Cannot resume subscription in '{subscription.status}' status (must be PAUSED)")

        now = utc_now()
        next_billing_utc = ensure_utc(subscription.next_billing_date)
        
        # If next_billing_date has already elapsed during pause, advance it from current time
        if next_billing_utc and next_billing_utc <= now:
            subscription.next_billing_date = calculate_next_billing_date(now, subscription.billing_frequency)

        subscription.status = "ACTIVE"
        subscription.paused_at = None
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def cancel_subscription(db: Session, subscription_id: uuid.UUID, reason: Optional[str] = None) -> Subscription:
        """Cancel an ACTIVE or PAUSED subscription."""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {subscription_id} not found")
        if subscription.status in ("CANCELED", "EXPIRED"):
            raise InvalidStateTransitionError(f"Subscription is already '{subscription.status}'")

        subscription.status = "CANCELED"
        subscription.canceled_at = utc_now()
        if reason:
            subscription.cancellation_reason = reason
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def renew_subscription(db: Session, subscription_id: uuid.UUID) -> Subscription:
        """Renew subscription by advancing next billing date and end date."""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            raise NotFoundError(f"Subscription {subscription_id} not found")
        if subscription.status == "CANCELED":
            raise InvalidStateTransitionError("Cannot renew a canceled subscription")

        now = utc_now()
        base_date = ensure_utc(subscription.next_billing_date) or now
        if base_date < now:
            base_date = now

        subscription.next_billing_date = calculate_next_billing_date(base_date, subscription.billing_frequency)
        if subscription.end_date:
            end_date_utc = ensure_utc(subscription.end_date)
            subscription.end_date = calculate_next_billing_date(end_date_utc, subscription.billing_frequency)

        subscription.status = "ACTIVE"
        db.commit()
        db.refresh(subscription)
        return subscription

