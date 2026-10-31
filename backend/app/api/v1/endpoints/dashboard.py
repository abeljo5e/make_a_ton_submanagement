from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_admin, require_staff, require_customer, get_current_active_user
from app.models.user import User
from app.services.dashboard_service import dashboard_service
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardRevenueResponse,
    DashboardSubscriptionsResponse,
    DashboardInvoicesResponse,
    CustomerDashboardResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get high-level dashboard KPI summary (Admin & Staff)",
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Return high-level summary KPIs for users, subscriptions, invoices, and revenue."""
    return dashboard_service.get_summary(db)


@router.get(
    "/revenue",
    response_model=DashboardRevenueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get monthly revenue trend series (Admin)",
)
def get_revenue(
    months: int = Query(default=12, ge=1, le=24, description="Number of months to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return monthly revenue for the last N months."""
    data = dashboard_service.get_revenue_series(db, months=months)
    return {"data": data}


@router.get(
    "/subscriptions",
    response_model=DashboardSubscriptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get subscription breakdown and recent subscriptions (Admin & Staff)",
)
def get_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Return subscription counts by status, breakdown by plan, and recent subscriptions."""
    return dashboard_service.get_subscriptions_metrics(db)


@router.get(
    "/invoices",
    response_model=DashboardInvoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get invoice payment metrics and recent invoices (Admin & Staff)",
)
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Return invoice payment status metrics, outstanding/paid amounts, and recent invoices."""
    return dashboard_service.get_invoices_metrics(db)


@router.get(
    "/customer",
    response_model=CustomerDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated customer's own subscription and invoices",
)
def get_customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    """Return current subscription, last 5 invoices, and available plans for the caller."""
    return dashboard_service.get_customer_dashboard(db, customer_id=current_user.id)

