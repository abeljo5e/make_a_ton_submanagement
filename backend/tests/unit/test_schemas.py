"""
Unit tests for Pydantic schemas: validation, decimal serialization, and defaults.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from pydantic import ValidationError

from app.schemas.quotation import QuotationCreate, QuotationLineCreate
from app.schemas.subscription import SubscriptionCreate, SubscriptionLineCreate
from app.schemas.payment import PaymentCreate


def test_quotation_create_schema_validation():
    customer_id = uuid.uuid4()
    payload = {
        "customer_id": customer_id,
        "currency": "INR",
        "lines": [
            {
                "description": "Standard SaaS",
                "quantity": 2,
                "unit_price": Decimal("500.00"),
                "discount_pct": Decimal("5.00"),
                "tax_rate_pct": Decimal("18.00"),
            }
        ],
    }
    schema = QuotationCreate(**payload)
    assert schema.customer_id == customer_id
    assert schema.currency == "INR"
    assert len(schema.lines) == 1
    assert schema.lines[0].unit_price == Decimal("500.00")


def test_quotation_create_invalid_quantity():
    with pytest.raises(ValidationError):
        QuotationLineCreate(
            description="Item",
            quantity=0,  # Must be > 0
            unit_price=Decimal("100.00"),
        )


def test_quotation_create_invalid_discount():
    with pytest.raises(ValidationError):
        QuotationLineCreate(
            description="Item",
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_pct=Decimal("150.00"),  # Must be <= 100
        )


def test_subscription_create_invalid_frequency():
    with pytest.raises(ValidationError):
        SubscriptionCreate(
            customer_id=uuid.uuid4(),
            plan_id=uuid.uuid4(),
            billing_frequency="hourly",  # invalid enum pattern
            currency="INR",
            start_date=datetime.now(timezone.utc),
            lines=[
                SubscriptionLineCreate(
                    description="Item",
                    quantity=1,
                    unit_price=Decimal("100.00"),
                )
            ],
        )


def test_payment_create_schema():
    invoice_id = uuid.uuid4()
    payment = PaymentCreate(
        invoice_id=invoice_id,
        amount=Decimal("500.00"),
        currency="INR",
        payment_method="simulation",
        payment_reference="SIM-001",
    )
    assert payment.amount == Decimal("500.00")
    assert payment.payment_method == "simulation"

