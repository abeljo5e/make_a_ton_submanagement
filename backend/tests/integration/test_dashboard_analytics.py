"""
Integration tests for Dashboard and Analytics endpoints.
Uses shared pytest fixtures from conftest.py: client, seeded_admin, seeded_staff, seeded_customer.
"""
import pytest


# ── Dashboard Tests ──────────────────────────────────────────────────────── #

def test_admin_can_access_summary(client, seeded_admin):
    resp = client.get("/api/v1/dashboard/summary", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("users", "customers", "active_subscriptions", "paused_subscriptions",
                "cancelled_subscriptions", "total_invoices", "outstanding_invoices", "revenue_total"):
        assert key in data


def test_staff_can_access_summary(client, seeded_staff):
    resp = client.get("/api/v1/dashboard/summary", headers=seeded_staff["headers"])
    assert resp.status_code == 200


def test_customer_cannot_access_summary(client, seeded_customer):
    resp = client.get("/api/v1/dashboard/summary", headers=seeded_customer["headers"])
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_summary(client):
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 401


def test_admin_gets_revenue_series(client, seeded_admin):
    resp = client.get("/api/v1/dashboard/revenue", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 12


def test_months_param_is_respected(client, seeded_admin):
    resp = client.get("/api/v1/dashboard/revenue?months=6", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 6


def test_staff_cannot_access_revenue(client, seeded_staff):
    resp = client.get("/api/v1/dashboard/revenue", headers=seeded_staff["headers"])
    assert resp.status_code == 403


def test_admin_gets_subscription_metrics(client, seeded_admin):
    resp = client.get("/api/v1/dashboard/subscriptions", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("by_status", "by_plan", "recent"):
        assert key in data


def test_admin_gets_invoice_metrics(client, seeded_admin):
    resp = client.get("/api/v1/dashboard/invoices", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("by_status", "outstanding_amount", "paid_amount", "recent"):
        assert key in data


def test_customer_gets_own_dashboard(client, seeded_customer):
    resp = client.get("/api/v1/dashboard/customer", headers=seeded_customer["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("subscription", "recent_invoices", "available_plans"):
        assert key in data


# ── Analytics Tests ──────────────────────────────────────────────────────── #

def test_admin_gets_analytics_revenue(client, seeded_admin):
    resp = client.get("/api/v1/analytics/revenue", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "total_revenue" in data
    assert "currency" in data


def test_analytics_revenue_item_keys(client, seeded_admin):
    resp = client.get("/api/v1/analytics/revenue?months=3", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 3
    for item in data["data"]:
        assert "month" in item
        assert "revenue" in item
        assert "invoice_count" in item


def test_admin_gets_subscription_analytics(client, seeded_admin):
    resp = client.get("/api/v1/analytics/subscriptions", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("growth", "status_breakdown", "plan_popularity"):
        assert key in data


def test_admin_gets_invoice_analytics(client, seeded_admin):
    resp = client.get("/api/v1/analytics/invoices", headers=seeded_admin["headers"])
    assert resp.status_code == 200
    data = resp.json()
    for key in ("monthly", "totals", "payment_rate"):
        assert key in data
    for key in ("paid_amount", "outstanding_amount", "cancelled_amount"):
        assert key in data["totals"]
