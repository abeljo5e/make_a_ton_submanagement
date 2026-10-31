import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductVariantCreate,
    ProductVariantUpdate,
    ProductVariantResponse,
)
from backend.app.services.product_service import (
    ProductService,
    ProductNotFoundError,
    ProductVariantNotFoundError,
)

router = APIRouter()


# --- Product Endpoints ---

@router.get("", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List / search products with optional filters and pagination.
    """
    service = ProductService(db)
    products, _ = service.list_products(
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        search=search,
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new product with optional initial variants.
    """
    service = ProductService(db)
    product = service.create_product(data)
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve product details and variants by product ID.
    """
    service = ProductService(db)
    try:
        product = service.get_product(product_id)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
):
    """
    Update product details.
    """
    service = ProductService(db)
    try:
        product = service.update_product(product_id, data)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.post("/{product_id}/deactivate", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def deactivate_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Deactivate a product (soft delete) to preserve quotation and subscription history.
    """
    service = ProductService(db)
    try:
        product = service.deactivate_product(product_id)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


# --- Variant Endpoints ---

@router.post("/{product_id}/variants", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    product_id: uuid.UUID,
    data: ProductVariantCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new variant to a product.
    """
    service = ProductService(db)
    try:
        variant = service.create_variant(product_id, data)
        return ProductVariantResponse.model_validate(variant)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )


@router.get("/{product_id}/variants", response_model=List[ProductVariantResponse], status_code=status.HTTP_200_OK)
def list_variants(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    List all variants for a specific product.
    """
    service = ProductService(db)
    try:
        product = service.get_product(product_id)
        return [ProductVariantResponse.model_validate(v) for v in product.variants]
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(e), "code": "NOT_FOUND"},
        )
