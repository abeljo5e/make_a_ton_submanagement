import uuid
from decimal import Decimal
import pytest

from backend.app.schemas.product import ProductCreate, ProductVariantCreate
from backend.app.schemas.plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    PlanProductInput,
)
from backend.app.services.product_service import ProductService
from backend.app.services.plan_service import (
    PlanService,
    PlanNotFoundError,
    PlanProductValidationError,
)


def test_create_and_retrieve_plan(db_session):
    prod_service = ProductService(db_session)
    plan_service = PlanService(db_session)

    # Create product and variant
    prod = prod_service.create_product(ProductCreate(name="Database Pro", sales_price=Decimal("800.00")))
    var = prod_service.create_variant(prod.id, ProductVariantCreate(name="High Memory", additional_price=Decimal("200.00")))

    # Create plan bundling product
    plan_in = SubscriptionPlanCreate(
        name="Developer Monthly",
        price=Decimal("950.00"),
        billing_frequency="monthly",
        minimum_quantity=1,
        auto_close=True,
        allow_early_cancellation=True,
        allow_pause=True,
        allow_renewal=True,
        products=[PlanProductInput(product_id=prod.id, variant_id=var.id, quantity=1)],
    )
    plan = plan_service.create_plan(plan_in)
    assert plan.id is not None
    assert plan.name == "Developer Monthly"
    assert plan.price == Decimal("950.00")
    assert plan.billing_interval == "monthly"
    assert len(plan.plan_products) == 1
    assert plan.plan_products[0].product_id == prod.id
    assert plan.plan_products[0].variant_id == var.id


def test_reject_invalid_bundled_product(db_session):
    plan_service = PlanService(db_session)
    fake_product_id = uuid.uuid4()

    plan_in = SubscriptionPlanCreate(
        name="Invalid Bundle",
        price=Decimal("500.00"),
        products=[PlanProductInput(product_id=fake_product_id, quantity=1)],
    )
    with pytest.raises(PlanProductValidationError) as exc_info:
        plan_service.create_plan(plan_in)
    assert "does not exist" in str(exc_info.value)


def test_add_and_remove_products_from_plan(db_session):
    prod_service = ProductService(db_session)
    plan_service = PlanService(db_session)

    p1 = prod_service.create_product(ProductCreate(name="Service A", sales_price=Decimal("100.00")))
    p2 = prod_service.create_product(ProductCreate(name="Service B", sales_price=Decimal("150.00")))

    plan = plan_service.create_plan(SubscriptionPlanCreate(name="Bundle Plan", price=Decimal("220.00")))
    assert len(plan.plan_products) == 0

    # Add p1 and p2 to plan
    updated_plan = plan_service.add_products_to_plan(
        plan.id,
        [
            PlanProductInput(product_id=p1.id, quantity=1),
            PlanProductInput(product_id=p2.id, quantity=2),
        ],
    )
    assert len(updated_plan.plan_products) == 2

    # Remove p1
    plan_after_removal = plan_service.remove_product_from_plan(plan.id, p1.id)
    assert len(plan_after_removal.plan_products) == 1
    assert plan_after_removal.plan_products[0].product_id == p2.id


def test_update_and_deactivate_plan(db_session):
    plan_service = PlanService(db_session)
    plan = plan_service.create_plan(SubscriptionPlanCreate(name="Growth Plan", price=Decimal("1200.00")))

    # Update
    updated = plan_service.update_plan(
        plan.id,
        SubscriptionPlanUpdate(price=Decimal("1400.00"), minimum_quantity=2),
    )
    assert updated.price == Decimal("1400.00")
    assert updated.minimum_quantity == 2

    # Deactivate
    deactivated = plan_service.deactivate_plan(plan.id)
    assert deactivated.is_active is False

    # Non-existent plan error
    with pytest.raises(PlanNotFoundError):
        plan_service.get_plan(uuid.uuid4())
