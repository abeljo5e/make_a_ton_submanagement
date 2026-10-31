import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    PlanProductInput,
)
from backend.app.services.plan_service import (
    PlanService,
    PlanNotFoundError,
    PlanProductValidationError,
)

router = APIRouter()


# --- Subscription Plan Endpoints ---

@router.get("", response_model=List[SubscriptionPlanResponse], status_code=status.HTTP_200_OK)
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    billing_frequency: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    available_only: bool = Query(False, description="Filter for customer catalogue to show only currently available plans"),
    db: Session = Depends(get_db),
):
    """
    List subscription plans with optional filtering and catalogue availability check.
    """
    service = PlanService(db)
    plans, _ = service.list_plans(
        skip=skip,
        limit=limit,
        billing_frequency=billing_frequency,
        is_active=is_active,
        search=search,
        only_currently_available=available_only,
    )
    return [SubscriptionPlanResponse.model_validate(p) for p in plans]


@router.post("", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new subscription plan with optional bundled products.
    """
    service = PlanService(db)
    try:
        plan = service.create_plan(data)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanProductValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"detail": str(e), "code": "VALIDATION_ERROR"},
        )


@router.get("/{plan_id}", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def get_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve plan details and bundled products by plan ID.
    """
    service = PlanService(db)
    try:
        plan = service.get_plan(plan_id)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.patch("/{plan_id}", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def update_plan(
    plan_id: uuid.UUID,
    data: SubscriptionPlanUpdate,
    db: Session = Depends(get_db),
):
    """
    Update plan details, pricing, or terms.
    """
    service = PlanService(db)
    try:
        plan = service.update_plan(plan_id, data)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.post("/{plan_id}/deactivate", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def deactivate_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Deactivate a plan instead of permanently deleting it to preserve customer subscriptions.
    """
    service = PlanService(db)
    try:
        plan = service.deactivate_plan(plan_id)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


# --- Plan-Product Association Endpoints ---

@router.post("/{plan_id}/products", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def add_products_to_plan(
    plan_id: uuid.UUID,
    products_input: List[PlanProductInput],
    db: Session = Depends(get_db),
):
    """
    Add or update bundled products in a subscription plan.
    """
    service = PlanService(db)
    try:
        plan = service.add_products_to_plan(plan_id, products_input)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )
    except PlanProductValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"detail": str(e), "code": "VALIDATION_ERROR"},
        )


@router.delete("/{plan_id}/products/{product_id}", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def remove_product_from_plan(
    plan_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Remove a product (and optional variant) from a subscription plan.
    """
    service = PlanService(db)
    try:
        plan = service.remove_product_from_plan(plan_id, product_id, variant_id)
        return SubscriptionPlanResponse.model_validate(plan)
    except PlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )
