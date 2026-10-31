"""
API endpoints for Subscriptions.
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.db.session import get_db
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create a subscription directly."""
    try:
        return SubscriptionService.create_subscription(db, data)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    customer_id: Optional[uuid.UUID] = Query(None),
    plan_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List subscriptions with optional filters."""
    items, _ = SubscriptionService.list_subscriptions(
        db, customer_id=customer_id, plan_id=plan_id, status=status, skip=skip, limit=limit
    )
    return items


@router.get("/{id}", response_model=SubscriptionResponse)
def get_subscription(id: uuid.UUID, db: Session = Depends(get_db)):
    """Get subscription by ID."""
    subscription = SubscriptionService.get_subscription(db, id)
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription {id} not found")
    return subscription


@router.post("/{id}/pause", response_model=SubscriptionResponse)
def pause_subscription(id: uuid.UUID, db: Session = Depends(get_db)):
    """Pause an active subscription."""
    try:
        return SubscriptionService.pause_subscription(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/resume", response_model=SubscriptionResponse)
def resume_subscription(id: uuid.UUID, db: Session = Depends(get_db)):
    """Resume a paused subscription."""
    try:
        return SubscriptionService.resume_subscription(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(id: uuid.UUID, reason: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Cancel an active or paused subscription."""
    try:
        return SubscriptionService.cancel_subscription(db, id, reason=reason)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/renew", response_model=SubscriptionResponse)
def renew_subscription(id: uuid.UUID, db: Session = Depends(get_db)):
    """Renew a subscription."""
    try:
        return SubscriptionService.renew_subscription(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

