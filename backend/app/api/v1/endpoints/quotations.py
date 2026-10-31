"""
API endpoints for Quotations.
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    ExpiredError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.session import get_db
from app.schemas.quotation import (
    QuotationCreate,
    QuotationResponse,
    QuotationUpdate,
)
from app.schemas.subscription import SubscriptionResponse
from app.services.quotation_service import QuotationService

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.post("", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_quotation(data: QuotationCreate, db: Session = Depends(get_db)):
    """Create a new quotation with line items."""
    try:
        return QuotationService.create_quotation(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[QuotationResponse])
def list_quotations(
    customer_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List quotations with optional filters and pagination."""
    items, _ = QuotationService.list_quotations(db, customer_id=customer_id, status=status, skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=QuotationResponse)
def get_quotation(id: uuid.UUID, db: Session = Depends(get_db)):
    """Fetch quotation by ID."""
    quotation = QuotationService.get_quotation(db, id)
    if not quotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quotation {id} not found")
    return quotation


@router.patch("/{id}", response_model=QuotationResponse)
def update_quotation(id: uuid.UUID, data: QuotationUpdate, db: Session = Depends(get_db)):
    """Update draft quotation metadata."""
    try:
        return QuotationService.update_quotation(db, id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/send", response_model=QuotationResponse)
def send_quotation(id: uuid.UUID, db: Session = Depends(get_db)):
    """Send draft quotation to customer (DRAFT -> SENT)."""
    try:
        return QuotationService.send_quotation(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidStateTransitionError, ExpiredError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/confirm", response_model=QuotationResponse)
def confirm_quotation(id: uuid.UUID, db: Session = Depends(get_db)):
    """Customer accepts/confirms quotation (SENT -> ACCEPTED)."""
    try:
        return QuotationService.accept_quotation(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidStateTransitionError, ExpiredError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/reject", response_model=QuotationResponse)
def reject_quotation(id: uuid.UUID, reason: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Customer or staff rejects quotation."""
    try:
        return QuotationService.reject_quotation(db, id, reason=reason)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/convert", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def convert_quotation(
    id: uuid.UUID,
    billing_frequency: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    """Convert an accepted quotation into an active subscription."""
    try:
        return QuotationService.convert_to_subscription(db, id, billing_frequency=billing_frequency)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
