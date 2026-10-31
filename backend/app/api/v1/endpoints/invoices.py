"""
API endpoints for Invoices.
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import InvoiceResponse
from app.services.billing_service import BillingService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    customer_id: Optional[uuid.UUID] = Query(None),
    subscription_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List invoices with optional filters and pagination."""
    items, _ = BillingService.list_invoices(
        db, customer_id=customer_id, subscription_id=subscription_id, status=status, skip=skip, limit=limit
    )
    return items


@router.get("/{id}", response_model=InvoiceResponse)
def get_invoice(id: uuid.UUID, db: Session = Depends(get_db)):
    """Get invoice details with lines and payment history."""
    invoice = BillingService.get_invoice(db, id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {id} not found")
    return invoice

