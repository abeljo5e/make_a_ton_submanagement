from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_admin, require_staff
from app.models.user import User
from app.services.analytics_service import analytics_service
from app.schemas.analytics import (
    AnalyticsRevenueResponse,
    AnalyticsSubscriptionsResponse,
    AnalyticsInvoicesResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/revenue",
    response_model=AnalyticsRevenueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get monthly revenue analytics and totals (Admin)",
)
def get_revenue_analytics(
    months: int = Query(default=12, ge=1, le=24, description="Time window in months"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Aggregate monthly paid revenue and transaction counts over the requested timeframe."""
    return analytics_service.get_revenue_analytics(db, months=months)


@router.get(
    "/subscriptions",
    response_model=AnalyticsSubscriptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get subscription growth and plan popularity trends (Admin & Staff)",
)
def get_subscription_analytics(
    months: int = Query(default=12, ge=1, le=24, description="Time window in months"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Aggregate monthly new subscriptions, current status breakdown, and plan popularity."""
    return analytics_service.get_subscription_analytics(db, months=months)


@router.get(
    "/invoices",
    response_model=AnalyticsInvoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get invoice payment metrics and collection rates (Admin & Staff)",
)
def get_invoice_analytics(
    months: int = Query(default=12, ge=1, le=24, description="Time window in months"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Aggregate monthly issued, paid, and outstanding counts, totals, and payment rate."""
    return analytics_service.get_invoice_analytics(db, months=months)
