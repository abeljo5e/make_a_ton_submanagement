import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import (
    ProductVariantUpdate,
    ProductVariantResponse,
)
from app.services.product_service import (
    ProductService,
    ProductVariantNotFoundError,
)

router = APIRouter()


@router.patch("/{variant_id}", response_model=ProductVariantResponse, status_code=status.HTTP_200_OK)
def update_variant(
    variant_id: uuid.UUID,
    data: ProductVariantUpdate,
    db: Session = Depends(get_db),
):
    """
    Update variant details.
    """
    service = ProductService(db)
    try:
        variant = service.update_variant(variant_id, data)
        return ProductVariantResponse.model_validate(variant)
    except ProductVariantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.delete("/{variant_id}", response_model=ProductVariantResponse, status_code=status.HTTP_200_OK)
def delete_or_deactivate_variant(
    variant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Deactivates a variant to preserve subscription and quotation line references safely.
    """
    service = ProductService(db)
    try:
        variant = service.deactivate_variant(variant_id)
        return ProductVariantResponse.model_validate(variant)
    except ProductVariantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )
