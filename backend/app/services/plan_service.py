import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session, selectinload

from backend.app.models.product import Product, ProductVariant
from backend.app.models.plan import SubscriptionPlan, PlanProduct
from backend.app.schemas.plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    PlanProductInput,
)


class PlanNotFoundError(Exception):
    def __init__(self, plan_id: uuid.UUID):
        super().__init__(f"Subscription plan with id '{plan_id}' not found.")
        self.plan_id = plan_id


class PlanProductValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def to_utc_datetime(d: Optional[date | datetime]) -> Optional[datetime]:
    if d is None:
        return None
    if isinstance(d, datetime):
        if d.tzinfo is None:
            return d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    return datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)


class PlanService:
    """
    Business logic service for Subscription Plans and Plan-Product Bundling (Member 2).
    """

    def __init__(self, session: Session):
        self.session = session

    # --- Plan Operations ---

    def create_plan(self, data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """
        Creates a new subscription plan and associates bundled products/variants.
        Validates that all included products and variants exist before committing.
        """
        # Validate included products/variants existence
        self._validate_bundled_products(data.products)

        interval_val = (
            data.billing_frequency.value
            if hasattr(data.billing_frequency, "value")
            else str(data.billing_frequency)
        )

        plan = SubscriptionPlan(
            name=data.name,
            description=data.description,
            price=data.price,
            currency=data.currency.upper(),
            billing_interval=interval_val,
            minimum_quantity=data.minimum_quantity,
            available_from=to_utc_datetime(data.available_from),
            available_until=to_utc_datetime(data.available_until),
            auto_close=data.auto_close,
            allow_early_cancellation=data.allow_early_cancellation,
            allow_pause=data.allow_pause,
            allow_renewal=data.allow_renewal,
            is_active=True,
        )

        if data.products:
            for item in data.products:
                plan_product = PlanProduct(
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                )
                plan.plan_products.append(plan_product)

        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan

    def get_plan(self, plan_id: uuid.UUID) -> SubscriptionPlan:
        """
        Retrieves a plan by ID with loaded products.
        Raises PlanNotFoundError if missing.
        """
        stmt = (
            select(SubscriptionPlan)
            .options(
                selectinload(SubscriptionPlan.plan_products).selectinload(PlanProduct.product),
                selectinload(SubscriptionPlan.plan_products).selectinload(PlanProduct.variant),
            )
            .where(SubscriptionPlan.id == plan_id)
        )
        plan = self.session.execute(stmt).scalar_one_or_none()
        if not plan:
            raise PlanNotFoundError(plan_id)
        return plan

    def list_plans(
        self,
        skip: int = 0,
        limit: int = 50,
        billing_frequency: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        only_currently_available: bool = False,
    ) -> Tuple[List[SubscriptionPlan], int]:
        """
        Lists plans with filtering, search, and availability checks.
        Returns (items, total_count).
        """
        filters = []
        if is_active is not None:
            filters.append(SubscriptionPlan.is_active == is_active)
        if billing_frequency:
            filters.append(SubscriptionPlan.billing_interval == billing_frequency.lower())
        if search:
            filters.append(SubscriptionPlan.name.ilike(f"%{search}%"))

        if only_currently_available:
            now = datetime.now(timezone.utc)
            filters.append(SubscriptionPlan.is_active == True)
            filters.append(
                or_(
                    SubscriptionPlan.available_from.is_(None),
                    SubscriptionPlan.available_from <= now,
                )
            )
            filters.append(
                or_(
                    SubscriptionPlan.available_until.is_(None),
                    SubscriptionPlan.available_until >= now,
                )
            )

        count_stmt = select(func.count(SubscriptionPlan.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = self.session.execute(count_stmt).scalar() or 0

        query_stmt = (
            select(SubscriptionPlan)
            .options(selectinload(SubscriptionPlan.plan_products))
            .order_by(SubscriptionPlan.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            query_stmt = query_stmt.where(and_(*filters))

        plans = list(self.session.execute(query_stmt).scalars().all())
        return plans, total

    def update_plan(self, plan_id: uuid.UUID, data: SubscriptionPlanUpdate) -> SubscriptionPlan:
        """
        Updates plan attributes.
        """
        plan = self.get_plan(plan_id)

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return plan

        if "name" in update_dict and update_dict["name"] is not None:
            plan.name = update_dict["name"]
        if "description" in update_dict:
            plan.description = update_dict["description"]
        if "price" in update_dict and update_dict["price"] is not None:
            plan.price = update_dict["price"]
        if "currency" in update_dict and update_dict["currency"] is not None:
            plan.currency = update_dict["currency"].upper()
        if "billing_frequency" in update_dict and update_dict["billing_frequency"] is not None:
            val = update_dict["billing_frequency"]
            plan.billing_interval = val.value if hasattr(val, "value") else str(val)
        if "minimum_quantity" in update_dict and update_dict["minimum_quantity"] is not None:
            plan.minimum_quantity = update_dict["minimum_quantity"]
        if "available_from" in update_dict:
            plan.available_from = to_utc_datetime(update_dict["available_from"])
        if "available_until" in update_dict:
            plan.available_until = to_utc_datetime(update_dict["available_until"])
        if "auto_close" in update_dict and update_dict["auto_close"] is not None:
            plan.auto_close = update_dict["auto_close"]
        if "allow_early_cancellation" in update_dict and update_dict["allow_early_cancellation"] is not None:
            plan.allow_early_cancellation = update_dict["allow_early_cancellation"]
        if "allow_pause" in update_dict and update_dict["allow_pause"] is not None:
            plan.allow_pause = update_dict["allow_pause"]
        if "allow_renewal" in update_dict and update_dict["allow_renewal"] is not None:
            plan.allow_renewal = update_dict["allow_renewal"]
        if "is_active" in update_dict and update_dict["is_active"] is not None:
            plan.is_active = update_dict["is_active"]

        self.session.commit()
        self.session.refresh(plan)
        return plan

    def deactivate_plan(self, plan_id: uuid.UUID) -> SubscriptionPlan:
        """
        Deactivates a plan instead of deleting it.
        """
        plan = self.get_plan(plan_id)
        plan.is_active = False
        self.session.commit()
        self.session.refresh(plan)
        return plan

    # --- Plan-Product Association Operations ---

    def add_products_to_plan(
        self,
        plan_id: uuid.UUID,
        products_input: List[PlanProductInput],
    ) -> SubscriptionPlan:
        """
        Adds or updates bundled products in an existing plan.
        """
        plan = self.get_plan(plan_id)
        self._validate_bundled_products(products_input)

        # Existing associations indexed by (product_id, variant_id)
        existing_map = {
            (pp.product_id, pp.variant_id): pp
            for pp in plan.plan_products
        }

        for item in products_input:
            key = (item.product_id, item.variant_id)
            if key in existing_map:
                # Update quantity if already present
                existing_map[key].quantity = item.quantity
            else:
                new_pp = PlanProduct(
                    plan_id=plan.id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                )
                self.session.add(new_pp)

        self.session.commit()
        self.session.refresh(plan)
        return plan

    def remove_product_from_plan(
        self,
        plan_id: uuid.UUID,
        product_id: uuid.UUID,
        variant_id: Optional[uuid.UUID] = None,
    ) -> SubscriptionPlan:
        """
        Removes a specific product (and optional variant) from a plan bundle.
        """
        plan = self.get_plan(plan_id)

        target = None
        for pp in plan.plan_products:
            if pp.product_id == product_id and pp.variant_id == variant_id:
                target = pp
                break

        if target:
            self.session.delete(target)
            self.session.commit()
            self.session.refresh(plan)

        return plan

    # --- Helpers ---

    def _validate_bundled_products(self, products: Optional[List[PlanProductInput]]) -> None:
        """
        Validates that referenced products and variants exist and are valid.
        """
        if not products:
            return

        for item in products:
            # Check product existence
            prod = self.session.execute(
                select(Product).where(Product.id == item.product_id)
            ).scalar_one_or_none()
            if not prod:
                raise PlanProductValidationError(
                    f"Referenced product '{item.product_id}' does not exist."
                )

            # If variant specified, verify existence and relationship
            if item.variant_id:
                variant = self.session.execute(
                    select(ProductVariant).where(
                        ProductVariant.id == item.variant_id,
                        ProductVariant.product_id == item.product_id,
                    )
                ).scalar_one_or_none()
                if not variant:
                    raise PlanProductValidationError(
                        f"Referenced variant '{item.variant_id}' does not exist or does not belong to product '{item.product_id}'."
                    )
