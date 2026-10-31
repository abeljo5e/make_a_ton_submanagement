"""
Quotation Service implementing Phase 3 business logic:
- Quotation creation with accurate line calculations
- Expiration and lifecycle management (DRAFT -> SENT -> ACCEPTED / REJECTED / EXPIRED)
- Idempotent conversion of accepted quotation to subscription
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
from app.db.base import utc_now, ensure_utc
from app.models.quotation import Quotation, QuotationLine
from app.models.subscription import Subscription, SubscriptionLine
from app.schemas.quotation import QuotationCreate, QuotationUpdate


class QuotationService:
    @staticmethod
    def generate_quotation_number(db: Session) -> str:
        """Generate human-readable unique quotation number like QT-202610-0001."""
        now = utc_now()
        prefix = f"QT-{now.strftime('%Y%m')}-"
        
        # Count existing quotations with this prefix
        stmt = select(func.count(Quotation.id)).where(Quotation.quotation_number.startswith(prefix))
        count = db.scalar(stmt) or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate) -> Quotation:
        """Create a new Quotation with calculated line item snapshots."""
        if not data.lines:
            raise ValueError("Quotation must have at least one line item")

        quotation_number = QuotationService.generate_quotation_number(db)
        quotation = Quotation(
            quotation_number=quotation_number,
            customer_id=data.customer_id,
            status="DRAFT",
            currency=data.currency,
            valid_until=data.valid_until,
            terms_and_conditions=data.terms_and_conditions,
            notes=data.notes,
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
            line = QuotationLine(
                quotation=quotation,
                plan_id=line_in.plan_id,
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
            quotation.lines.append(line)
            subtotal += calc.subtotal
            discount_amount += calc.discount_amount
            tax_amount += calc.tax_amount
            total_amount += calc.total_amount

        quotation.subtotal = quantize_money(subtotal)
        quotation.discount_amount = quantize_money(discount_amount)
        quotation.tax_amount = quantize_money(tax_amount)
        quotation.total_amount = quantize_money(total_amount)

        db.add(quotation)
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def get_quotation(db: Session, quotation_id: uuid.UUID) -> Optional[Quotation]:
        """Fetch a quotation by ID with its line items eagerly loaded."""
        stmt = (
            select(Quotation)
            .where(Quotation.id == quotation_id)
            .options(selectinload(Quotation.lines), selectinload(Quotation.subscription))
        )
        return db.scalar(stmt)

    @staticmethod
    def list_quotations(
        db: Session,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Quotation], int]:
        """List quotations with optional filters and pagination."""
        stmt = select(Quotation).options(selectinload(Quotation.lines)).order_by(Quotation.created_at.desc())
        count_stmt = select(func.count(Quotation.id))

        if customer_id:
            stmt = stmt.where(Quotation.customer_id == customer_id)
            count_stmt = count_stmt.where(Quotation.customer_id == customer_id)
        if status:
            stmt = stmt.where(Quotation.status == status.upper())
            count_stmt = count_stmt.where(Quotation.status == status.upper())

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total

    @staticmethod
    def update_quotation(db: Session, quotation_id: uuid.UUID, data: QuotationUpdate) -> Quotation:
        """Update draft quotation metadata."""
        quotation = QuotationService.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError(f"Quotation {quotation_id} not found")
        if quotation.status not in ("DRAFT", "SENT"):
            raise InvalidStateTransitionError(f"Cannot edit quotation in '{quotation.status}' status")

        if data.valid_until is not None:
            quotation.valid_until = data.valid_until
        if data.terms_and_conditions is not None:
            quotation.terms_and_conditions = data.terms_and_conditions
        if data.notes is not None:
            quotation.notes = data.notes

        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def send_quotation(db: Session, quotation_id: uuid.UUID) -> Quotation:
        """Transition quotation from DRAFT to SENT."""
        quotation = QuotationService.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError(f"Quotation {quotation_id} not found")
        if quotation.status != "DRAFT":
            raise InvalidStateTransitionError(f"Cannot send quotation in '{quotation.status}' status")

        # Check if already expired
        now = utc_now()
        valid_until_utc = ensure_utc(quotation.valid_until)
        if valid_until_utc and valid_until_utc < now:
            quotation.status = "EXPIRED"
            db.commit()
            raise ExpiredError("Cannot send an expired quotation")

        quotation.status = "SENT"
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def accept_quotation(db: Session, quotation_id: uuid.UUID) -> Quotation:
        """Customer accepts quotation. Allowed from SENT or DRAFT."""
        quotation = QuotationService.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError(f"Quotation {quotation_id} not found")
        if quotation.status not in ("DRAFT", "SENT"):
            raise InvalidStateTransitionError(f"Cannot accept quotation in '{quotation.status}' status")

        now = utc_now()
        valid_until_utc = ensure_utc(quotation.valid_until)
        if valid_until_utc and valid_until_utc < now:
            quotation.status = "EXPIRED"
            db.commit()
            raise ExpiredError("Quotation has expired and cannot be accepted")

        quotation.status = "ACCEPTED"
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def reject_quotation(db: Session, quotation_id: uuid.UUID, reason: Optional[str] = None) -> Quotation:
        """Customer or staff marks quotation as REJECTED."""
        quotation = QuotationService.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError(f"Quotation {quotation_id} not found")
        if quotation.status not in ("DRAFT", "SENT"):
            raise InvalidStateTransitionError(f"Cannot reject quotation in '{quotation.status}' status")

        quotation.status = "REJECTED"
        if reason:
            quotation.notes = f"{quotation.notes or ''}\nRejection Reason: {reason}".strip()
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def expire_stale_quotations(db: Session, current_time: Optional[datetime] = None) -> int:
        """Expire all active quotations whose valid_until date has passed."""
        now = current_time or utc_now()
        stmt = (
            select(Quotation)
            .where(
                Quotation.status.in_(["DRAFT", "SENT"]),
                Quotation.valid_until.isnot(None),
                Quotation.valid_until < now,
            )
        )
        stale = list(db.scalars(stmt).all())
        for q in stale:
            q.status = "EXPIRED"
        db.commit()
        return len(stale)

    @staticmethod
    def convert_to_subscription(
        db: Session,
        quotation_id: uuid.UUID,
        plan_id: Optional[uuid.UUID] = None,
        billing_frequency: str = "monthly",
        start_date: Optional[datetime] = None,
    ) -> Subscription:
        """
        Convert an ACCEPTED quotation into an ACTIVE subscription.
        Guarantees idempotency (only one subscription per quotation).
        """
        quotation = QuotationService.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError(f"Quotation {quotation_id} not found")
        if quotation.status != "ACCEPTED":
            raise InvalidStateTransitionError(
                f"Quotation must be in 'ACCEPTED' status to convert, currently '{quotation.status}'"
            )

        # Idempotency check: verify no subscription exists with this quotation_id
        existing_sub = db.scalar(select(Subscription).where(Subscription.quotation_id == quotation_id))
        if existing_sub:
            raise ConflictError(f"Quotation {quotation_id} has already been converted to subscription {existing_sub.subscription_number}")

        # Determine plan_id: either explicitly supplied or extracted from first line
        resolved_plan_id = plan_id
        if not resolved_plan_id:
            for line in quotation.lines:
                if line.plan_id:
                    resolved_plan_id = line.plan_id
                    break
        if not resolved_plan_id:
            # Fallback to customer UUID or generate placeholder UUID if plan wasn't specified on lines
            resolved_plan_id = uuid.uuid4()

        start = start_date or utc_now()
        next_billing = calculate_next_billing_date(start, billing_frequency)

        # Generate unique subscription number
        now = utc_now()
        prefix = f"SUB-{now.strftime('%Y%m')}-"
        count = db.scalar(select(func.count(Subscription.id)).where(Subscription.subscription_number.startswith(prefix))) or 0
        subscription_number = f"{prefix}{count + 1:04d}"

        subscription = Subscription(
            subscription_number=subscription_number,
            customer_id=quotation.customer_id,
            plan_id=resolved_plan_id,
            quotation_id=quotation.id,
            status="ACTIVE",
            billing_frequency=billing_frequency,
            currency=quotation.currency,
            subtotal=quotation.subtotal,
            discount_amount=quotation.discount_amount,
            tax_amount=quotation.tax_amount,
            total_amount=quotation.total_amount,
            start_date=start,
            next_billing_date=next_billing,
            auto_renew=True,
        )

        for q_line in quotation.lines:
            sub_line = SubscriptionLine(
                subscription=subscription,
                product_id=q_line.product_id,
                variant_id=q_line.variant_id,
                description=q_line.description,
                quantity=q_line.quantity,
                unit_price=q_line.unit_price,
                discount_pct=q_line.discount_pct,
                discount_amount=q_line.discount_amount,
                tax_rate_pct=q_line.tax_rate_pct,
                tax_amount=q_line.tax_amount,
                total_amount=q_line.total_amount,
            )
            subscription.lines.append(sub_line)

        quotation.status = "CONVERTED"
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
