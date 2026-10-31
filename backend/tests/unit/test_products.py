import uuid
from decimal import Decimal
import pytest

from app.schemas.product import ProductCreate, ProductVariantCreate
from app.services.product_service import ProductService, ProductNotFoundError, ProductVariantNotFoundError


def test_create_product_with_variants(db_session):
    service = ProductService(db_session)
    product_in = ProductCreate(
        name="CRM Enterprise",
        type="software",
        sales_price=Decimal("1500.00"),
        cost_price=Decimal("500.00"),
        currency="INR",
        variants=[
            ProductVariantCreate(name="Multi-tenant", additional_price=Decimal("350.00")),
            ProductVariantCreate(name="Custom Domain", additional_price=Decimal("150.00")),
        ],
    )
    product = service.create_product(product_in)
    assert product.id is not None
    assert product.name == "CRM Enterprise"
    assert product.sales_price == Decimal("1500.00")
    assert product.category == "software"
    assert product.is_active is True
    assert len(product.variants) == 2
    assert product.variants[0].additional_price == Decimal("350.00")


def test_get_and_list_products(db_session):
    service = ProductService(db_session)
    p1 = service.create_product(ProductCreate(name="Alpha App", sales_price=Decimal("100.00")))
    p2 = service.create_product(ProductCreate(name="Beta App", sales_price=Decimal("200.00")))

    # Retrieve by ID
    retrieved = service.get_product(p1.id)
    assert retrieved.name == "Alpha App"

    # List all
    items, total = service.list_products()
    assert total == 2
    assert len(items) == 2

    # Filter by search
    items_search, total_search = service.list_products(search="Beta")
    assert total_search == 1
    assert items_search[0].name == "Beta App"


def test_update_and_deactivate_product(db_session):
    service = ProductService(db_session)
    product = service.create_product(ProductCreate(name="Initial Name", sales_price=Decimal("100.00")))

    # Update
    from app.schemas.product import ProductUpdate
    updated = service.update_product(product.id, ProductUpdate(name="Updated Name", sales_price=Decimal("150.00")))
    assert updated.name == "Updated Name"
    assert updated.sales_price == Decimal("150.00")

    # Deactivate
    deactivated = service.deactivate_product(product.id)
    assert deactivated.is_active is False

    # Check listing with active filter
    active_items, count = service.list_products(is_active=True)
    assert count == 0


def test_variant_lifecycle(db_session):
    service = ProductService(db_session)
    product = service.create_product(ProductCreate(name="Base Product", sales_price=Decimal("50.00")))

    # Add variant
    variant = service.create_variant(
        product.id,
        ProductVariantCreate(name="Pro Tier", additional_price=Decimal("25.00")),
    )
    assert variant.name == "Pro Tier"
    assert variant.product_id == product.id

    # Update variant
    from app.schemas.product import ProductVariantUpdate
    updated_var = service.update_variant(variant.id, ProductVariantUpdate(name="Pro Max"))
    assert updated_var.name == "Pro Max"

    # Deactivate variant
    deactivated_var = service.deactivate_variant(variant.id)
    assert deactivated_var.is_active is False


def test_nonexistent_product_or_variant_raises_error(db_session):
    service = ProductService(db_session)
    non_existent_id = uuid.uuid4()

    with pytest.raises(ProductNotFoundError):
        service.get_product(non_existent_id)

    with pytest.raises(ProductVariantNotFoundError):
        service.get_variant(non_existent_id)
