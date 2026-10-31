"""
Payment Service implementing payment recording and invoice reconciliation.
Supports partial and full payments, balance updates, and status transitions.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.calculations import (
    evaluate_invoice_payment_status,
    quantize_money,
)
from app.core.exceptions import (
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.base import ensure_utc, utc_now
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


class PaymentService:
    @staticmethod
    def generate_payment_number(db: Session) -> str:
        """Generate human-readable unique payment number like PAY-202610-0001."""
        now = utc_now()
        prefix = f"PAY-{now.strftime('%Y%m')}-"
        count = db.scalar(select(func.count(Payment.id)).where(Payment.payment_number.startswith(prefix))) or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    def record_payment(db: Session, data: PaymentCreate) -> Payment:
        """
        Record a payment against an invoice and reconcile the invoice balance.
        """
        if data.amount <= Decimal("0.00"):
            raise ValueError("Payment amount must be greater than zero")

        invoice = db.scalar(
            select(Invoice)
            .where(Invoice.id == data.invoice_id)
            .options(selectinload(Invoice.payments))
        )
        if not invoice:
            raise NotFoundError(f"Invoice {data.invoice_id} not found")

        if invoice.status == "CANCELED":
            raise InvalidStateTransitionError("Cannot record payment against a canceled invoice")

        payment_number = PaymentService.generate_payment_number(db)
        payment_amount = quantize_money(data.amount)

        payment = Payment(
            payment_number=payment_number,
            invoice_id=invoice.id,
            amount=payment_amount,
            currency=data.currency,
            payment_method=data.payment_method,
            payment_reference=data.payment_reference,
            payment_status=data.payment_status,
            payment_date=utc_now(),
            notes=data.notes,
        )

        db.add(payment)
        
        # Only successful payments reduce balance due
        if data.payment_status.upper() == "SUCCESS":
            invoice.amount_paid = quantize_money(invoice.amount_paid + payment_amount)
            new_balance = invoice.total_amount - invoice.amount_paid
            invoice.balance_due = quantize_money(max(Decimal("0.00"), new_balance))
            invoice.status = evaluate_invoice_payment_status(invoice.total_amount, invoice.amount_paid)

        db.commit()
        db.refresh(payment)
        db.refresh(invoice)
        return payment

    @staticmethod
    def get_payment(db: Session, payment_id: uuid.UUID) -> Optional[Payment]:
        """Fetch a payment by ID."""
        return db.scalar(select(Payment).where(Payment.id == payment_id).options(selectinload(Payment.invoice)))

    @staticmethod
    def list_payments(
        db: Session,
        invoice_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Payment], int]:
        """List payments with optional invoice filter and pagination."""
        stmt = select(Payment).order_by(Payment.payment_date.desc())
        count_stmt = select(func.count(Payment.id))

        if invoice_id:
            stmt = stmt.where(Payment.invoice_id == invoice_id)
            count_stmt = count_stmt.where(Payment.invoice_id == invoice_id)

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
