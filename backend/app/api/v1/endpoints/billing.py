"""
API endpoints for Recurring Billing Runs.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.billing import BillingRunRequest, BillingRunResponse
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/run", response_model=BillingRunResponse, status_code=status.HTTP_200_OK)
def trigger_billing_run(data: BillingRunRequest = None, db: Session = Depends(get_db)):
    """Trigger a recurring billing execution."""
    run_date = data.run_date if data else None
    return BillingService.process_recurring_billing_run(db, run_date=run_date, trigger_type="MANUAL")

