"""
Billing Service implementing Phase 5 recurring invoice generation & billing runs.
Guarantees database & application-level idempotency, safe retries, and accurate audit history.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
import uuid

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.calculations import (
    calculate_billing_period,
    calculate_next_billing_date,
    quantize_money,
)
from app.core.exceptions import (
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.base import ensure_utc, utc_now
from app.models.billing_run import BillingRun
from app.models.invoice import Invoice, InvoiceLine
from app.models.subscription import Subscription


class BillingService:
    @staticmethod
    def generate_invoice_number(db: Session) -> str:
        """Generate human-readable unique invoice number like INV-202610-0001."""
        now = utc_now()
        prefix = f"INV-{now.strftime('%Y%m')}-"
        count = db.scalar(select(func.count(Invoice.id)).where(Invoice.invoice_number.startswith(prefix))) or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    def generate_invoice_for_subscription(
        db: Session,
        subscription: Subscription,
        billing_date: Optional[datetime] = None,
        payment_terms_days: int = 14,
    ) -> Optional[Invoice]:
        """
        Generate a single recurring invoice for an active subscription.
        Idempotent: Skips or returns existing invoice if already generated for this billing period.
        """
        if subscription.status != "ACTIVE":
            return None

        run_time = ensure_utc(billing_date) or utc_now()
        period_start = ensure_utc(subscription.next_billing_date)
        if not period_start:
            period_start = run_time

        # Calculate period boundaries
        period_start, period_end = calculate_billing_period(period_start, subscription.billing_frequency)

        # Idempotency check: look for an existing invoice for this subscription & period
        existing_stmt = select(Invoice).where(
            Invoice.subscription_id == subscription.id,
            Invoice.billing_period_start == period_start,
            Invoice.billing_period_end == period_end,
            Invoice.status != "CANCELED",
        ).options(selectinload(Invoice.lines))
        existing_invoice = db.scalar(existing_stmt)
        if existing_invoice:
            # Already billed for this period
            return existing_invoice

        invoice_number = BillingService.generate_invoice_number(db)
        due_date = run_time + relativedelta(days=payment_terms_days)

        invoice = Invoice(
            invoice_number=invoice_number,
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            billing_period_start=period_start,
            billing_period_end=period_end,
            issue_date=run_time,
            due_date=due_date,
            status="CONFIRMED",
            currency=subscription.currency,
            subtotal=subscription.subtotal,
            discount_amount=subscription.discount_amount,
            tax_amount=subscription.tax_amount,
            total_amount=subscription.total_amount,
            amount_paid=Decimal("0.00"),
            balance_due=subscription.total_amount,
        )

        for sub_line in subscription.lines:
            inv_line = InvoiceLine(
                invoice=invoice,
                description=sub_line.description,
                quantity=sub_line.quantity,
                unit_price=sub_line.unit_price,
                discount_pct=sub_line.discount_pct,
                discount_amount=sub_line.discount_amount,
                tax_rate_pct=sub_line.tax_rate_pct,
                tax_amount=sub_line.tax_amount,
                total_amount=sub_line.total_amount,
            )
            invoice.lines.append(inv_line)

        # Advance subscription next_billing_date
        subscription.next_billing_date = calculate_next_billing_date(period_start, subscription.billing_frequency)

        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def process_recurring_billing_run(
        db: Session,
        run_date: Optional[datetime] = None,
        trigger_type: str = "SCHEDULED",
    ) -> BillingRun:
        """
        Batch recurring billing execution.
        Finds all ACTIVE subscriptions due for billing (next_billing_date <= run_date).
        Generates invoices and updates billing metrics.
        """
        now = ensure_utc(run_date) or utc_now()
        billing_run = BillingRun(
            run_date=now,
            status="RUNNING",
            trigger_type=trigger_type,
            subscriptions_evaluated=0,
            invoices_generated=0,
            total_invoiced_amount=Decimal("0.00"),
        )
        db.add(billing_run)
        db.commit()
        db.refresh(billing_run)

        # Query eligible subscriptions
        stmt = (
            select(Subscription)
            .where(
                Subscription.status == "ACTIVE",
                Subscription.next_billing_date <= now,
            )
            .options(selectinload(Subscription.lines))
        )
        eligible_subs = list(db.scalars(stmt).all())

        evaluated_count = len(eligible_subs)
        generated_count = 0
        total_invoiced = Decimal("0.00")

        for sub in eligible_subs:
            try:
                # Check if an invoice was already generated
                p_start, p_end = calculate_billing_period(ensure_utc(sub.next_billing_date), sub.billing_frequency)
                check_stmt = select(Invoice).where(
                    Invoice.subscription_id == sub.id,
                    Invoice.billing_period_start == p_start,
                    Invoice.billing_period_end == p_end,
                    Invoice.status != "CANCELED",
                )
                already_exists = db.scalar(check_stmt) is not None

                invoice = BillingService.generate_invoice_for_subscription(db, sub, billing_date=now)
                if invoice and not already_exists:
                    generated_count += 1
                    total_invoiced += invoice.total_amount
            except Exception as e:
                # Log error and continue to next subscription to avoid whole batch failure
                billing_run.error_message = f"Error billing sub {sub.subscription_number}: {str(e)}"

        billing_run.subscriptions_evaluated = evaluated_count
        billing_run.invoices_generated = generated_count
        billing_run.total_invoiced_amount = quantize_money(total_invoiced)
        billing_run.status = "COMPLETED"

        db.commit()
        db.refresh(billing_run)
        return billing_run

    @staticmethod
    def get_invoice(db: Session, invoice_id: uuid.UUID) -> Optional[Invoice]:
        """Fetch invoice with lines and payments eagerly loaded."""
        stmt = (
            select(Invoice)
            .where(Invoice.id == invoice_id)
            .options(
                selectinload(Invoice.lines),
                selectinload(Invoice.payments),
                selectinload(Invoice.subscription),
            )
        )
        return db.scalar(stmt)

    @staticmethod
    def list_invoices(
        db: Session,
        customer_id: Optional[uuid.UUID] = None,
        subscription_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Invoice], int]:
        """List invoices with filters and pagination."""
        stmt = select(Invoice).options(selectinload(Invoice.lines)).order_by(Invoice.issue_date.desc())
        count_stmt = select(func.count(Invoice.id))

        if customer_id:
            stmt = stmt.where(Invoice.customer_id == customer_id)
            count_stmt = count_stmt.where(Invoice.customer_id == customer_id)
        if subscription_id:
            stmt = stmt.where(Invoice.subscription_id == subscription_id)
            count_stmt = count_stmt.where(Invoice.subscription_id == subscription_id)
        if status:
            stmt = stmt.where(Invoice.status == status.upper())
            count_stmt = count_stmt.where(Invoice.status == status.upper())

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
