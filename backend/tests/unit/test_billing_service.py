"""
Unit tests for BillingService and PaymentService (Phase 5).
Validates recurring invoice generation, billing runs, idempotency safety, and payment settlement.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import InvalidStateTransitionError, NotFoundError
from app.db.base import Base, ensure_utc
from app.schemas.payment import PaymentCreate
from app.schemas.subscription import SubscriptionCreate, SubscriptionLineCreate
from app.services.billing_service import BillingService
from app.services.payment_service import PaymentService
from app.services.subscription_service import SubscriptionService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_generate_invoice_for_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    start_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    sub = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=start_date,
            lines=[
                SubscriptionLineCreate(
                    description="Standard Cloud Instance",
                    quantity=2,
                    unit_price=Decimal("1500.00"),
                    tax_rate_pct=Decimal("18.00"),
                )
            ],
        ),
    )
    # Next billing date is set to 2026-12-01
    assert ensure_utc(sub.next_billing_date) == datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Generate invoice for that billing date
    invoice = BillingService.generate_invoice_for_subscription(db_session, sub, billing_date=sub.next_billing_date)
    assert invoice is not None
    assert invoice.invoice_number.startswith("INV-")
    assert invoice.status == "CONFIRMED"
    assert invoice.subtotal == Decimal("3000.00")
    assert invoice.tax_amount == Decimal("540.00")
    assert invoice.total_amount == Decimal("3540.00")
    assert invoice.balance_due == Decimal("3540.00")
    assert invoice.amount_paid == Decimal("0.00")
    assert len(invoice.lines) == 1
    assert invoice.lines[0].description == "Standard Cloud Instance"

    # Verify subscription next_billing_date was advanced to 2027-01-01
    assert ensure_utc(sub.next_billing_date) == datetime(2027, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_billing_idempotency_prevents_duplicate_invoice(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    start_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    sub = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=start_date,
            lines=[SubscriptionLineCreate(description="Service", quantity=1, unit_price=Decimal("1000.00"))],
        ),
    )
    billing_date = sub.next_billing_date

    # First generation
    inv1 = BillingService.generate_invoice_for_subscription(db_session, sub, billing_date=billing_date)
    assert inv1 is not None

    # Reset subscription's next_billing_date to test re-running the same period
    sub.next_billing_date = billing_date
    db_session.commit()

    # Second generation attempt must return the existing invoice (Idempotency)
    inv2 = BillingService.generate_invoice_for_subscription(db_session, sub, billing_date=billing_date)
    assert inv2.id == inv1.id
    assert inv2.invoice_number == inv1.invoice_number


def test_recurring_billing_run_batch(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    now = datetime(2026, 11, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # Subscription 1: Due for billing (next_billing_date is 2026-11-01)
    sub1 = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc),
            lines=[SubscriptionLineCreate(description="Plan A", quantity=1, unit_price=Decimal("1000.00"))],
        ),
    )

    # Subscription 2: Due for billing (next_billing_date is 2026-11-01)
    sub2 = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc),
            lines=[SubscriptionLineCreate(description="Plan B", quantity=1, unit_price=Decimal("2000.00"))],
        ),
    )

    # Subscription 3: Not due yet (next_billing_date in December)
    sub3 = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
            lines=[SubscriptionLineCreate(description="Plan C", quantity=1, unit_price=Decimal("3000.00"))],
        ),
    )

    # Execute billing run for 2026-11-01
    run = BillingService.process_recurring_billing_run(db_session, run_date=now)
    assert run.status == "COMPLETED"
    assert run.subscriptions_evaluated == 2
    assert run.invoices_generated == 2
    # Total invoiced = 1000.00 + 2000.00 = 3000.00
    assert run.total_invoiced_amount == Decimal("3000.00")

    # Retrying the same billing run should generate 0 additional invoices (Idempotent)
    retry_run = BillingService.process_recurring_billing_run(db_session, run_date=now)
    assert retry_run.invoices_generated == 0


def test_payment_settlement_workflow(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    sub = SubscriptionService.create_subscription(
        db_session,
        SubscriptionCreate(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_frequency="monthly",
            start_date=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
            lines=[SubscriptionLineCreate(description="Service", quantity=1, unit_price=Decimal("1000.00"))],
        ),
    )
    invoice = BillingService.generate_invoice_for_subscription(db_session, sub)
    assert invoice.status == "CONFIRMED"
    assert invoice.total_amount == Decimal("1000.00")
    assert invoice.balance_due == Decimal("1000.00")

    # 1. Partial payment of 400.00
    p1 = PaymentService.record_payment(
        db_session,
        PaymentCreate(
            invoice_id=invoice.id,
            amount=Decimal("400.00"),
            payment_method="upi",
            payment_reference="UPI-001",
        ),
    )
    assert p1.payment_number.startswith("PAY-")
    assert invoice.status == "PARTIALLY_PAID"
    assert invoice.amount_paid == Decimal("400.00")
    assert invoice.balance_due == Decimal("600.00")

    # 2. Final payment of remaining 600.00
    p2 = PaymentService.record_payment(
        db_session,
        PaymentCreate(
            invoice_id=invoice.id,
            amount=Decimal("600.00"),
            payment_method="bank_transfer",
            payment_reference="NEFT-002",
        ),
    )
    assert invoice.status == "PAID"
    assert invoice.amount_paid == Decimal("1000.00")
    assert invoice.balance_due == Decimal("0.00")
    assert len(invoice.payments) == 2


def test_payment_validation_and_errors(db_session: Session):
    # Non-existent invoice
    with pytest.raises(NotFoundError):
        PaymentService.record_payment(
            db_session,
            PaymentCreate(
                invoice_id=uuid.uuid4(),
                amount=Decimal("100.00"),
                payment_reference="REF-001",
            ),
        )

    # Invalid non-positive amount
    with pytest.raises(ValueError, match="greater than"):
        PaymentCreate(
            invoice_id=uuid.uuid4(),
            amount=Decimal("0.00"),
            payment_reference="REF-002",
        )
