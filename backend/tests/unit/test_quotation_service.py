"""
Unit tests for QuotationService (Phase 3).
Validates line math, lifecycle state machine, expiration enforcement, and quotation conversion.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import (
    ConflictError,
    ExpiredError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.base import Base, ensure_utc
from app.schemas.quotation import QuotationCreate, QuotationLineCreate
from app.services.quotation_service import QuotationService


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


def test_create_quotation_and_verify_financial_totals(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    future_date = datetime.now(timezone.utc) + relativedelta(days=30)

    data = QuotationCreate(
        customer_id=customer_id,
        currency="INR",
        valid_until=future_date,
        lines=[
            QuotationLineCreate(
                plan_id=plan_id,
                description="Enterprise Cloud Base",
                quantity=2,
                unit_price=Decimal("1000.00"),
                discount_pct=Decimal("10.00"),  # 200.00 discount
                tax_rate_pct=Decimal("18.00"),  # 18% of 1800.00 = 324.00
            ),
            QuotationLineCreate(
                description="Premium Support Add-on",
                quantity=1,
                unit_price=Decimal("500.00"),
                discount_pct=Decimal("0.00"),
                tax_rate_pct=Decimal("18.00"),  # 18% of 500.00 = 90.00
            ),
        ],
    )

    quotation = QuotationService.create_quotation(db_session, data)
    assert quotation is not None
    assert quotation.quotation_number.startswith("QT-")
    assert quotation.status == "DRAFT"
    
    # Subtotal = 2000.00 + 500.00 = 2500.00
    assert quotation.subtotal == Decimal("2500.00")
    # Discount = 200.00 + 0.00 = 200.00
    assert quotation.discount_amount == Decimal("200.00")
    # Tax = 324.00 + 90.00 = 414.00
    assert quotation.tax_amount == Decimal("414.00")
    # Total = 2500.00 - 200.00 + 414.00 = 2714.00
    assert quotation.total_amount == Decimal("2714.00")
    assert len(quotation.lines) == 2


def test_quotation_lifecycle_sent_and_accepted(db_session: Session):
    customer_id = uuid.uuid4()
    future_date = datetime.now(timezone.utc) + relativedelta(days=14)
    data = QuotationCreate(
        customer_id=customer_id,
        valid_until=future_date,
        lines=[
            QuotationLineCreate(
                description="Standard Plan",
                quantity=1,
                unit_price=Decimal("1500.00"),
            )
        ],
    )
    quotation = QuotationService.create_quotation(db_session, data)
    assert quotation.status == "DRAFT"

    # Send quotation
    sent_q = QuotationService.send_quotation(db_session, quotation.id)
    assert sent_q.status == "SENT"

    # Accept quotation
    accepted_q = QuotationService.accept_quotation(db_session, quotation.id)
    assert accepted_q.status == "ACCEPTED"


def test_quotation_rejection_with_reason(db_session: Session):
    customer_id = uuid.uuid4()
    data = QuotationCreate(
        customer_id=customer_id,
        lines=[
            QuotationLineCreate(
                description="Custom Plan",
                quantity=1,
                unit_price=Decimal("3000.00"),
            )
        ],
    )
    quotation = QuotationService.create_quotation(db_session, data)
    QuotationService.send_quotation(db_session, quotation.id)

    rejected_q = QuotationService.reject_quotation(
        db_session,
        quotation.id,
        reason="Price exceeds quarterly departmental budget",
    )
    assert rejected_q.status == "REJECTED"
    assert "Price exceeds quarterly departmental budget" in rejected_q.notes


def test_expired_quotation_cannot_be_accepted(db_session: Session):
    customer_id = uuid.uuid4()
    past_date = datetime.now(timezone.utc) - relativedelta(days=5)
    data = QuotationCreate(
        customer_id=customer_id,
        valid_until=past_date,
        lines=[
            QuotationLineCreate(
                description="Expired Service",
                quantity=1,
                unit_price=Decimal("1000.00"),
            )
        ],
    )
    quotation = QuotationService.create_quotation(db_session, data)

    # Attempting to accept an expired quotation raises ExpiredError
    with pytest.raises(ExpiredError, match="expired"):
        QuotationService.accept_quotation(db_session, quotation.id)

    # Status should now be EXPIRED
    refreshed = QuotationService.get_quotation(db_session, quotation.id)
    assert refreshed.status == "EXPIRED"


def test_expire_stale_quotations_job(db_session: Session):
    customer_id = uuid.uuid4()
    past_date = datetime.now(timezone.utc) - relativedelta(days=2)
    future_date = datetime.now(timezone.utc) + relativedelta(days=10)

    # Stale quotation
    data_stale = QuotationCreate(
        customer_id=customer_id,
        valid_until=past_date,
        lines=[QuotationLineCreate(description="Stale Item", quantity=1, unit_price=Decimal("100.00"))],
    )
    q_stale = QuotationService.create_quotation(db_session, data_stale)
    
    # Active quotation
    data_active = QuotationCreate(
        customer_id=customer_id,
        valid_until=future_date,
        lines=[QuotationLineCreate(description="Active Item", quantity=1, unit_price=Decimal("100.00"))],
    )
    q_active = QuotationService.create_quotation(db_session, data_active)

    expired_count = QuotationService.expire_stale_quotations(db_session)
    assert expired_count == 1

    assert QuotationService.get_quotation(db_session, q_stale.id).status == "EXPIRED"
    assert QuotationService.get_quotation(db_session, q_active.id).status == "DRAFT"


def test_convert_accepted_quotation_to_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    data = QuotationCreate(
        customer_id=customer_id,
        lines=[
            QuotationLineCreate(
                plan_id=plan_id,
                description="Business Monthly Plan",
                quantity=1,
                unit_price=Decimal("2000.00"),
                tax_rate_pct=Decimal("18.00"),
            )
        ],
    )
    quotation = QuotationService.create_quotation(db_session, data)
    QuotationService.send_quotation(db_session, quotation.id)
    QuotationService.accept_quotation(db_session, quotation.id)

    # Convert to subscription
    start_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    subscription = QuotationService.convert_to_subscription(
        db_session,
        quotation_id=quotation.id,
        billing_frequency="monthly",
        start_date=start_date,
    )

    assert subscription is not None
    assert subscription.subscription_number.startswith("SUB-")
    assert subscription.status == "ACTIVE"
    assert subscription.quotation_id == quotation.id
    assert ensure_utc(subscription.start_date) == start_date
    assert ensure_utc(subscription.next_billing_date) == datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert subscription.total_amount == quotation.total_amount
    assert len(subscription.lines) == 1
    assert subscription.lines[0].description == "Business Monthly Plan"

    # Quotation status must now be CONVERTED
    refreshed_q = QuotationService.get_quotation(db_session, quotation.id)
    assert refreshed_q.status == "CONVERTED"


def test_cannot_convert_twice_or_unaccepted_quotation(db_session: Session):
    customer_id = uuid.uuid4()
    data = QuotationCreate(
        customer_id=customer_id,
        lines=[QuotationLineCreate(description="Plan", quantity=1, unit_price=Decimal("1000.00"))],
    )
    quotation = QuotationService.create_quotation(db_session, data)

    # Attempting to convert DRAFT quotation raises InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError, match="must be in 'ACCEPTED' status"):
        QuotationService.convert_to_subscription(db_session, quotation.id)

    # Accept it
    QuotationService.send_quotation(db_session, quotation.id)
    QuotationService.accept_quotation(db_session, quotation.id)

    # First conversion succeeds
    QuotationService.convert_to_subscription(db_session, quotation.id)

    # Second conversion attempt raises ConflictError (Idempotency)
    with pytest.raises(InvalidStateTransitionError):
        # Already in CONVERTED status
        QuotationService.convert_to_subscription(db_session, quotation.id)
