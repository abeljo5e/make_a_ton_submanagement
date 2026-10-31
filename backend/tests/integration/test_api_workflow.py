"""
End-to-End API Integration tests for Member 3's complete billing workflow:
Health -> Quotation Creation -> Confirmation -> Subscription Conversion ->
Pause/Resume -> Recurring Billing Run -> Invoice Generation -> Payment Settlement.
"""
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Create shared in-memory database for API integration tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_complete_end_to_end_quotation_to_payment_lifecycle():
    customer_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())

    # 1. Create a Quotation
    quotation_payload = {
        "customer_id": customer_id,
        "currency": "INR",
        "valid_until": (datetime.now(timezone.utc) + relativedelta(days=30)).isoformat(),
        "lines": [
            {
                "plan_id": plan_id,
                "description": "Brightloop Enterprise Suite",
                "quantity": 2,
                "unit_price": "2500.00",
                "discount_pct": "10.00",  # Subtotal 5000 - 500 discount = 4500
                "tax_rate_pct": "18.00",  # 18% of 4500 = 810 tax -> Total 5310.00
            }
        ],
    }
    q_res = client.post("/api/v1/quotations", json=quotation_payload)
    assert q_res.status_code == 201
    q_data = q_res.json()
    quotation_id = q_data["id"]
    assert q_data["status"] == "DRAFT"
    assert q_data["subtotal"] == "5000.00"
    assert q_data["discount_amount"] == "500.00"
    assert q_data["tax_amount"] == "810.00"
    assert q_data["total_amount"] == "5310.00"

    # 2. Send Quotation
    send_res = client.post(f"/api/v1/quotations/{quotation_id}/send")
    assert send_res.status_code == 200
    assert send_res.json()["status"] == "SENT"

    # 3. Customer Confirms Quotation
    confirm_res = client.post(f"/api/v1/quotations/{quotation_id}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "ACCEPTED"

    # 4. Convert to Active Subscription
    convert_res = client.post(f"/api/v1/quotations/{quotation_id}/convert?billing_frequency=monthly")
    assert convert_res.status_code == 201
    sub_data = convert_res.json()
    subscription_id = sub_data["id"]
    assert sub_data["status"] == "ACTIVE"
    assert sub_data["total_amount"] == "5310.00"
    assert len(sub_data["lines"]) == 1

    # 5. Pause and Resume Subscription
    pause_res = client.post(f"/api/v1/subscriptions/{subscription_id}/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    resume_res = client.post(f"/api/v1/subscriptions/{subscription_id}/resume")
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "ACTIVE"

    # 6. Trigger Recurring Billing Run for subscription due date
    next_billing_str = resume_res.json()["next_billing_date"]
    billing_res = client.post("/api/v1/billing/run", json={"run_date": next_billing_str})
    assert billing_res.status_code == 200
    b_data = billing_res.json()
    assert b_data["status"] == "COMPLETED"
    assert b_data["invoices_generated"] >= 1

    # 7. List Invoices
    inv_list_res = client.get(f"/api/v1/invoices?subscription_id={subscription_id}")
    assert inv_list_res.status_code == 200
    invoices = inv_list_res.json()
    assert len(invoices) >= 1
    invoice = invoices[0]
    invoice_id = invoice["id"]
    assert invoice["status"] == "CONFIRMED"
    assert invoice["total_amount"] == "5310.00"
    assert invoice["balance_due"] == "5310.00"

    # 8. Record Partial Payment (3000.00)
    pay1_payload = {
        "invoice_id": invoice_id,
        "amount": "3000.00",
        "payment_method": "upi",
        "payment_reference": "UPI-TRANS-98765",
    }
    p1_res = client.post("/api/v1/payments", json=pay1_payload)
    assert p1_res.status_code == 201
    
    # Check invoice status is now PARTIALLY_PAID
    inv_check1 = client.get(f"/api/v1/invoices/{invoice_id}").json()
    assert inv_check1["status"] == "PARTIALLY_PAID"
    assert inv_check1["amount_paid"] == "3000.00"
    assert inv_check1["balance_due"] == "2310.00"

    # 9. Record Final Payment (2310.00)
    pay2_payload = {
        "invoice_id": invoice_id,
        "amount": "2310.00",
        "payment_method": "bank_transfer",
        "payment_reference": "NEFT-TRANS-54321",
    }
    p2_res = client.post("/api/v1/payments", json=pay2_payload)
    assert p2_res.status_code == 201

    # Check invoice status is now PAID with 0.00 balance
    inv_check2 = client.get(f"/api/v1/invoices/{invoice_id}").json()
    assert inv_check2["status"] == "PAID"
    assert inv_check2["amount_paid"] == "5310.00"
    assert inv_check2["balance_due"] == "0.00"

    # 10. List Payments
    payments_res = client.get(f"/api/v1/payments?invoice_id={invoice_id}")
    assert payments_res.status_code == 200
    assert len(payments_res.json()) == 2
