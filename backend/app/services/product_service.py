import uuid
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, ProductVariant
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantUpdate,
)


class ProductNotFoundError(Exception):
    def __init__(self, product_id: uuid.UUID):
        super().__init__(f"Product with id '{product_id}' not found.")
        self.product_id = product_id


class ProductVariantNotFoundError(Exception):
    def __init__(self, variant_id: uuid.UUID):
        super().__init__(f"Product variant with id '{variant_id}' not found.")
        self.variant_id = variant_id


class ProductService:
    """
    Business logic service for Products and Product Variants (Member 2).
    """

    def __init__(self, session: Session):
        self.session = session

    # --- Product Operations ---

    def create_product(self, data: ProductCreate) -> Product:
        """
        Creates a new product in the catalog with optional initial variants.
        """
        category_val = data.category or data.type

        product = Product(
            name=data.name,
            description=data.description,
            category=category_val,
            sales_price=data.sales_price,
            cost_price=data.cost_price,
            currency=data.currency.upper(),
            is_active=True,
        )

        if data.variants:
            for v_data in data.variants:
                variant = ProductVariant(
                    name=v_data.name,
                    description=v_data.description,
                    additional_price=v_data.additional_price,
                    is_active=True,
                )
                product.variants.append(variant)

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_product(self, product_id: uuid.UUID) -> Product:
        """
        Retrieves a product by ID including its variants.
        Raises ProductNotFoundError if not found.
        """
        stmt = (
            select(Product)
            .options(selectinload(Product.variants))
            .where(Product.id == product_id)
        )
        product = self.session.execute(stmt).scalar_one_or_none()
        if not product:
            raise ProductNotFoundError(product_id)
        return product

    def list_products(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Product], int]:
        """
        Lists products with optional filtering, search, and pagination.
        Returns a tuple of (items, total_count).
        """
        filters = []
        if is_active is not None:
            filters.append(Product.is_active == is_active)
        if category:
            filters.append(Product.category.ilike(f"%{category}%"))
        if search:
            filters.append(Product.name.ilike(f"%{search}%"))

        count_stmt = select(func.count(Product.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = self.session.execute(count_stmt).scalar() or 0

        query_stmt = (
            select(Product)
            .options(selectinload(Product.variants))
            .order_by(Product.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            query_stmt = query_stmt.where(and_(*filters))

        products = list(self.session.execute(query_stmt).scalars().all())
        return products, total

    def update_product(self, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        """
        Updates product fields.
        """
        product = self.get_product(product_id)

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return product

        if "name" in update_dict and update_dict["name"] is not None:
            product.name = update_dict["name"]
        if "description" in update_dict:
            product.description = update_dict["description"]
        if "category" in update_dict:
            product.category = update_dict["category"]
        elif "type" in update_dict:
            product.category = update_dict["type"]
        if "sales_price" in update_dict and update_dict["sales_price"] is not None:
            product.sales_price = update_dict["sales_price"]
        if "cost_price" in update_dict and update_dict["cost_price"] is not None:
            product.cost_price = update_dict["cost_price"]
        if "currency" in update_dict and update_dict["currency"] is not None:
            product.currency = update_dict["currency"].upper()
        if "is_active" in update_dict and update_dict["is_active"] is not None:
            product.is_active = update_dict["is_active"]

        self.session.commit()
        self.session.refresh(product)
        return product

    def deactivate_product(self, product_id: uuid.UUID) -> Product:
        """
        Soft-deactivates a product instead of permanently deleting it.
        Preserves referential integrity for existing quotations and subscriptions.
        """
        product = self.get_product(product_id)
        product.is_active = False
        self.session.commit()
        self.session.refresh(product)
        return product

    # --- Variant Operations ---

    def create_variant(self, product_id: uuid.UUID, data: ProductVariantCreate) -> ProductVariant:
        """
        Creates a new variant under an existing product.
        """
        # Ensure parent product exists
        product = self.get_product(product_id)

        variant = ProductVariant(
            product_id=product.id,
            name=data.name,
            description=data.description,
            additional_price=data.additional_price,
            is_active=True,
        )
        self.session.add(variant)
        self.session.commit()
        self.session.refresh(variant)
        return variant

    def get_variant(self, variant_id: uuid.UUID) -> ProductVariant:
        """
        Retrieves a single product variant by ID.
        """
        stmt = select(ProductVariant).where(ProductVariant.id == variant_id)
        variant = self.session.execute(stmt).scalar_one_or_none()
        if not variant:
            raise ProductVariantNotFoundError(variant_id)
        return variant

    def update_variant(self, variant_id: uuid.UUID, data: ProductVariantUpdate) -> ProductVariant:
        """
        Updates variant details.
        """
        variant = self.get_variant(variant_id)

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return variant

        if "name" in update_dict and update_dict["name"] is not None:
            variant.name = update_dict["name"]
        if "description" in update_dict:
            variant.description = update_dict["description"]
        if "additional_price" in update_dict and update_dict["additional_price"] is not None:
            variant.additional_price = update_dict["additional_price"]
        if "is_active" in update_dict and update_dict["is_active"] is not None:
            variant.is_active = update_dict["is_active"]

        self.session.commit()
        self.session.refresh(variant)
        return variant

    def deactivate_variant(self, variant_id: uuid.UUID) -> ProductVariant:
        """
        Deactivates a variant instead of permanently deleting it.
        """
        variant = self.get_variant(variant_id)
        variant.is_active = False
        self.session.commit()
        self.session.refresh(variant)
        return variant
