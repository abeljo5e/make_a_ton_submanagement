"""
Unit tests for SubscriptionService (Phase 4).
Validates direct subscription creation, state transitions, pause/resume, cancellation, and renewal.
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
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.base import Base, ensure_utc
from app.schemas.subscription import SubscriptionCreate, SubscriptionLineCreate
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


def test_create_subscription_directly(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    start_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    data = SubscriptionCreate(
        customer_id=customer_id,
        plan_id=plan_id,
        billing_frequency="monthly",
        currency="INR",
        start_date=start_date,
        lines=[
            SubscriptionLineCreate(
                description="Professional Monthly Plan",
                quantity=1,
                unit_price=Decimal("2500.00"),
                tax_rate_pct=Decimal("18.00"),
            )
        ],
    )

    sub = SubscriptionService.create_subscription(db_session, data)
    assert sub is not None
    assert sub.subscription_number.startswith("SUB-")
    assert sub.status == "ACTIVE"
    assert sub.subtotal == Decimal("2500.00")
    assert sub.tax_amount == Decimal("450.00")
    assert sub.total_amount == Decimal("2950.00")
    assert ensure_utc(sub.start_date) == start_date
    assert ensure_utc(sub.next_billing_date) == datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert len(sub.lines) == 1


def test_pause_and_resume_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    start_date = datetime.now(timezone.utc)

    data = SubscriptionCreate(
        customer_id=customer_id,
        plan_id=plan_id,
        billing_frequency="monthly",
        start_date=start_date,
        lines=[SubscriptionLineCreate(description="Service", quantity=1, unit_price=Decimal("1000.00"))],
    )
    sub = SubscriptionService.create_subscription(db_session, data)
    assert sub.status == "ACTIVE"

    # Pause
    paused_sub = SubscriptionService.pause_subscription(db_session, sub.id)
    assert paused_sub.status == "PAUSED"
    assert paused_sub.paused_at is not None

    # Cannot pause again
    with pytest.raises(InvalidStateTransitionError):
        SubscriptionService.pause_subscription(db_session, sub.id)

    # Resume
    resumed_sub = SubscriptionService.resume_subscription(db_session, sub.id)
    assert resumed_sub.status == "ACTIVE"
    assert resumed_sub.paused_at is None

    # Cannot resume again
    with pytest.raises(InvalidStateTransitionError):
        SubscriptionService.resume_subscription(db_session, sub.id)


def test_cancel_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    data = SubscriptionCreate(
        customer_id=customer_id,
        plan_id=plan_id,
        billing_frequency="yearly",
        start_date=datetime.now(timezone.utc),
        lines=[SubscriptionLineCreate(description="Annual Plan", quantity=1, unit_price=Decimal("12000.00"))],
    )
    sub = SubscriptionService.create_subscription(db_session, data)

    canceled_sub = SubscriptionService.cancel_subscription(
        db_session,
        sub.id,
        reason="Switching to on-premise deployment",
    )
    assert canceled_sub.status == "CANCELED"
    assert canceled_sub.canceled_at is not None
    assert canceled_sub.cancellation_reason == "Switching to on-premise deployment"

    # Cannot cancel again
    with pytest.raises(InvalidStateTransitionError):
        SubscriptionService.cancel_subscription(db_session, sub.id)


def test_renew_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    start_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    data = SubscriptionCreate(
        customer_id=customer_id,
        plan_id=plan_id,
        billing_frequency="monthly",
        start_date=start_date,
        lines=[SubscriptionLineCreate(description="Monthly Service", quantity=1, unit_price=Decimal("500.00"))],
    )
    sub = SubscriptionService.create_subscription(db_session, data)
    assert ensure_utc(sub.next_billing_date) == datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Renew advances next_billing_date by 1 month
    renewed_sub = SubscriptionService.renew_subscription(db_session, sub.id)
    assert ensure_utc(renewed_sub.next_billing_date) == datetime(2027, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_cannot_renew_canceled_subscription(db_session: Session):
    customer_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    data = SubscriptionCreate(
        customer_id=customer_id,
        plan_id=plan_id,
        billing_frequency="monthly",
        start_date=datetime.now(timezone.utc),
        lines=[SubscriptionLineCreate(description="Service", quantity=1, unit_price=Decimal("500.00"))],
    )
    sub = SubscriptionService.create_subscription(db_session, data)
    SubscriptionService.cancel_subscription(db_session, sub.id)

    with pytest.raises(InvalidStateTransitionError, match="Cannot renew a canceled subscription"):
        SubscriptionService.renew_subscription(db_session, sub.id)

