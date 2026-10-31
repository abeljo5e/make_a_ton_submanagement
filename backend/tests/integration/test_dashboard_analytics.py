import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, Customer, UserRole
from app.core.security import create_access_token, hash_password


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


@pytest.fixture(scope="module")
def setup_users():
    """Seed test users into database and generate bearer tokens."""
    db = TestingSessionLocal()
    
    admin_id = uuid.uuid4()
    staff_id = uuid.uuid4()
    customer_id = uuid.uuid4()

    admin = User(
        id=admin_id,
        full_name="Alex Mercer",
        email="admin@brightloop.test",
        password_hash=hash_password("Admin@123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    staff = User(
        id=staff_id,
        full_name="Sarah Connor",
        email="staff@brightloop.test",
        password_hash=hash_password("Staff@123"),
        role=UserRole.STAFF,
        is_active=True,
    )
    customer_user = User(
        id=customer_id,
        full_name="John Doe",
        email="customer@brightloop.test",
        password_hash=hash_password("Customer@123"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    cust_profile = Customer(
        user_id=customer_id,
        company_name="Acme Corp",
        phone="+919876543210",
    )

    db.add_all([admin, staff, customer_user, cust_profile])
    db.commit()
    db.close()

    admin_token = create_access_token({"sub": str(admin_id), "role": "admin"})
    staff_token = create_access_token({"sub": str(staff_id), "role": "staff"})
    customer_token = create_access_token({"sub": str(customer_id), "role": "customer"})

    return {
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "staff_headers": {"Authorization": f"Bearer {staff_token}"},
        "customer_headers": {"Authorization": f"Bearer {customer_token}"},
    }


# ── Dashboard Tests ──────────────────────────────────────────────────────── #

def test_admin_can_access_summary(setup_users):
    resp = client.get("/api/v1/dashboard/summary", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("users", "customers", "active_subscriptions", "paused_subscriptions",
                "cancelled_subscriptions", "total_invoices", "outstanding_invoices", "revenue_total"):
        assert key in data


def test_staff_can_access_summary(setup_users):
    resp = client.get("/api/v1/dashboard/summary", headers=setup_users["staff_headers"])
    assert resp.status_code == 200


def test_customer_cannot_access_summary(setup_users):
    resp = client.get("/api/v1/dashboard/summary", headers=setup_users["customer_headers"])
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_summary():
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 401


def test_admin_gets_revenue_series(setup_users):
    resp = client.get("/api/v1/dashboard/revenue", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 12


def test_months_param_is_respected(setup_users):
    resp = client.get("/api/v1/dashboard/revenue?months=6", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 6


def test_staff_cannot_access_revenue(setup_users):
    resp = client.get("/api/v1/dashboard/revenue", headers=setup_users["staff_headers"])
    assert resp.status_code == 403


def test_admin_gets_subscription_metrics(setup_users):
    resp = client.get("/api/v1/dashboard/subscriptions", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("by_status", "by_plan", "recent"):
        assert key in data


def test_admin_gets_invoice_metrics(setup_users):
    resp = client.get("/api/v1/dashboard/invoices", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("by_status", "outstanding_amount", "paid_amount", "recent"):
        assert key in data


def test_customer_gets_own_dashboard(setup_users):
    resp = client.get("/api/v1/dashboard/customer", headers=setup_users["customer_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("subscription", "recent_invoices", "available_plans"):
        assert key in data


# ── Analytics Tests ──────────────────────────────────────────────────────── #

def test_admin_gets_analytics_revenue(setup_users):
    resp = client.get("/api/v1/analytics/revenue", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "total_revenue" in data
    assert "currency" in data


def test_analytics_revenue_item_keys(setup_users):
    resp = client.get("/api/v1/analytics/revenue?months=3", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 3
    for item in data["data"]:
        assert "month" in item
        assert "revenue" in item
        assert "invoice_count" in item


def test_admin_gets_subscription_analytics(setup_users):
    resp = client.get("/api/v1/analytics/subscriptions", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("growth", "status_breakdown", "plan_popularity"):
        assert key in data


def test_admin_gets_invoice_analytics(setup_users):
    resp = client.get("/api/v1/analytics/invoices", headers=setup_users["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("monthly", "totals", "payment_rate"):
        assert key in data
    for key in ("paid_amount", "outstanding_amount", "cancelled_amount"):
        assert key in data["totals"]

