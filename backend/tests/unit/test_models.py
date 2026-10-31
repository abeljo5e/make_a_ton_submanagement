"""
Unit and schema tests for Member 3 SQLAlchemy models.
Validates table creation, foreign keys, relationships, cascades, and idempotency constraints.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.quotation import Quotation, QuotationLine
from app.models.subscription import Subscription, SubscriptionLine
from app.models.invoice import Invoice, InvoiceLine
from app.models.payment import Payment
from app.models.billing_run import BillingRun


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing SQLAlchemy models."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_create_quotation_with_lines(db_session: Session):
    customer_id = uuid.uuid4()
    quotation = Quotation(
        quotation_number="QT-2026-0001",
        customer_id=customer_id,
        status="DRAFT",
        currency="INR",
        subtotal=Decimal("1000.00"),
        discount_amount=Decimal("100.00"),
        tax_amount=Decimal("162.00"),
        total_amount=Decimal("1062.00"),
        valid_until=datetime(2026, 12, 31, tzinfo=timezone.utc),
    )
    line1 = QuotationLine(
        quotation=quotation,
        description="Brightloop Cloud ERP - Annual",
        quantity=2,
        unit_price=Decimal("500.00"),
        discount_pct=Decimal("10.00"),
        discount_amount=Decimal("100.00"),
        tax_rate_pct=Decimal("18.00"),
        tax_amount=Decimal("162.00"),
        total_amount=Decimal("1062.00"),
    )
    db_session.add(quotation)
    db_session.commit()

    saved_quotation = db_session.scalar(select(Quotation).where(Quotation.quotation_number == "QT-2026-0001"))
    assert saved_quotation is not None
    assert len(saved_quotation.lines) == 1
    assert saved_quotation.lines[0].description == "Brightloop Cloud ERP - Annual"
    assert saved_quotation.lines[0].total_amount == Decimal("1062.00")


def test_create_subscription_and_convert_quotation(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    quotation = Quotation(
        quotation_number="QT-2026-0002",
        customer_id=customer_id,
        status="ACCEPTED",
        subtotal=Decimal("2500.00"),
        total_amount=Decimal("2500.00"),
    )
    db_session.add(quotation)
    db_session.commit()

    subscription = Subscription(
        subscription_number="SUB-2026-0001",
        customer_id=customer_id,
        plan_id=plan_id,
        quotation_id=quotation.id,
        status="ACTIVE",
        billing_frequency="monthly",
        currency="INR",
        subtotal=Decimal("2500.00"),
        total_amount=Decimal("2500.00"),
        start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        next_billing_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    sub_line = SubscriptionLine(
        subscription=subscription,
        description="Professional Plan Monthly",
        quantity=1,
        unit_price=Decimal("2500.00"),
        total_amount=Decimal("2500.00"),
    )
    db_session.add(subscription)
    db_session.commit()

    saved_sub = db_session.scalar(select(Subscription).where(Subscription.subscription_number == "SUB-2026-0001"))
    assert saved_sub is not None
    assert saved_sub.quotation_id == quotation.id
    assert saved_sub.quotation.quotation_number == "QT-2026-0002"
    assert len(saved_sub.lines) == 1


def test_quotation_conversion_idempotency_prevents_duplicates(db_session: Session):
    """Enforce that one quotation cannot be converted into two distinct subscriptions."""
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    quotation = Quotation(
        quotation_number="QT-2026-0003",
        customer_id=customer_id,
        status="ACCEPTED",
        subtotal=Decimal("1500.00"),
        total_amount=Decimal("1500.00"),
    )
    db_session.add(quotation)
    db_session.commit()

    sub1 = Subscription(
        subscription_number="SUB-2026-0002",
        customer_id=customer_id,
        plan_id=plan_id,
        quotation_id=quotation.id,
        status="ACTIVE",
        start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        next_billing_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add(sub1)
    db_session.commit()

    sub2 = Subscription(
        subscription_number="SUB-2026-0003",
        customer_id=customer_id,
        plan_id=plan_id,
        quotation_id=quotation.id,  # Duplicate quotation reference!
        status="ACTIVE",
        start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        next_billing_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add(sub2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_invoice_creation_and_payment_settlement(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    sub = Subscription(
        subscription_number="SUB-2026-0004",
        customer_id=customer_id,
        plan_id=plan_id,
        status="ACTIVE",
        start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        next_billing_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add(sub)
    db_session.commit()

    period_start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    period_end = datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone.utc)
    
    invoice = Invoice(
        invoice_number="INV-2026-0001",
        subscription_id=sub.id,
        customer_id=customer_id,
        billing_period_start=period_start,
        billing_period_end=period_end,
        issue_date=period_start,
        due_date=datetime(2026, 11, 15, tzinfo=timezone.utc),
        status="CONFIRMED",
        subtotal=Decimal("2000.00"),
        total_amount=Decimal("2000.00"),
        amount_paid=Decimal("0.00"),
        balance_due=Decimal("2000.00"),
    )
    inv_line = InvoiceLine(
        invoice=invoice,
        description="November Subscription Fee",
        quantity=1,
        unit_price=Decimal("2000.00"),
        total_amount=Decimal("2000.00"),
    )
    db_session.add(invoice)
    db_session.commit()

    # Record partial payment
    pay1 = Payment(
        payment_number="PAY-2026-0001",
        invoice=invoice,
        amount=Decimal("1000.00"),
        payment_method="upi",
        payment_reference="UPI-REF-12345",
        payment_date=datetime.now(timezone.utc),
    )
    db_session.add(pay1)
    invoice.amount_paid += pay1.amount
    invoice.balance_due -= pay1.amount
    invoice.status = "PARTIALLY_PAID"
    db_session.commit()

    saved_invoice = db_session.scalar(select(Invoice).where(Invoice.invoice_number == "INV-2026-0001"))
    assert saved_invoice.status == "PARTIALLY_PAID"
    assert saved_invoice.amount_paid == Decimal("1000.00")
    assert saved_invoice.balance_due == Decimal("1000.00")
    assert len(saved_invoice.payments) == 1

    # Record remaining payment
    pay2 = Payment(
        payment_number="PAY-2026-0002",
        invoice=invoice,
        amount=Decimal("1000.00"),
        payment_method="bank_transfer",
        payment_reference="NEFT-REF-67890",
        payment_date=datetime.now(timezone.utc),
    )
    db_session.add(pay2)
    invoice.amount_paid += pay2.amount
    invoice.balance_due -= pay2.amount
    invoice.status = "PAID"
    db_session.commit()

    assert saved_invoice.status == "PAID"
    assert saved_invoice.balance_due == Decimal("0.00")
    assert len(saved_invoice.payments) == 2


def test_invoice_billing_period_idempotency_constraint(db_session: Session):
    """Enforce that two invoices cannot be created for the same subscription and period."""
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    sub = Subscription(
        subscription_number="SUB-2026-0005",
        customer_id=customer_id,
        plan_id=plan_id,
        status="ACTIVE",
        start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
        next_billing_date=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add(sub)
    db_session.commit()

    period_start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    period_end = datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone.utc)

    inv1 = Invoice(
        invoice_number="INV-2026-0002",
        subscription_id=sub.id,
        customer_id=customer_id,
        billing_period_start=period_start,
        billing_period_end=period_end,
        issue_date=period_start,
        due_date=period_start,
        total_amount=Decimal("1000.00"),
        balance_due=Decimal("1000.00"),
    )
    db_session.add(inv1)
    db_session.commit()

    # Attempt duplicate invoice for same subscription & period
    inv2 = Invoice(
        invoice_number="INV-2026-0003",
        subscription_id=sub.id,
        customer_id=customer_id,
        billing_period_start=period_start,
        billing_period_end=period_end,
        issue_date=period_start,
        due_date=period_start,
        total_amount=Decimal("1000.00"),
        balance_due=Decimal("1000.00"),
    )
    db_session.add(inv2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_billing_run(db_session: Session):
    run = BillingRun(
        run_date=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        status="COMPLETED",
        trigger_type="SCHEDULED",
        subscriptions_evaluated=5,
        invoices_generated=3,
        total_invoiced_amount=Decimal("7500.00"),
    )
    db_session.add(run)
    db_session.commit()

    saved_run = db_session.scalar(select(BillingRun).where(BillingRun.id == run.id))
    assert saved_run is not None
    assert saved_run.subscriptions_evaluated == 5
    assert saved_run.invoices_generated == 3
    assert saved_run.total_invoiced_amount == Decimal("7500.00")
