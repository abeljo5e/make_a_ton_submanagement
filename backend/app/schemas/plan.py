import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def format_decimal(v: Decimal | float | int | str | None) -> str:
    if v is None:
        return "0.00"
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return f"{Decimal(str(v)):.2f}"


class BillingFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


# --- Plan Product Association Schemas ---

class PlanProductInput(BaseModel):
    product_id: uuid.UUID = Field(..., description="UUID of the product to include")
    variant_id: Optional[uuid.UUID] = Field(None, description="Optional variant UUID")
    quantity: int = Field(default=1, ge=1, description="Quantity included in plan")


class PlanProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    quantity: int = 1


# --- Subscription Plan Schemas ---

class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        description="Plan price per billing frequency"
    )
    currency: str = Field(default="INR", min_length=3, max_length=3, description="ISO 4217 Currency code")
    billing_frequency: BillingFrequency = Field(
        default=BillingFrequency.MONTHLY,
        description="Billing frequency interval"
    )
    minimum_quantity: int = Field(default=1, ge=1, description="Minimum subscription quantity")
    available_from: Optional[date | datetime] = Field(None, description="Start date of plan availability")
    available_until: Optional[date | datetime] = Field(None, description="End date of plan availability")

    # Policy flags
    auto_close: bool = Field(default=True, description="Auto-close overdue subscription")
    allow_early_cancellation: bool = Field(default=True, description="Permit early cancellation")
    allow_pause: bool = Field(default=True, description="Permit pausing subscription")
    allow_renewal: bool = Field(default=True, description="Permit renewal")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Plan name cannot be empty or whitespace only")
        return stripped

    @model_validator(mode="before")
    @classmethod
    def sync_frequency_and_interval(cls, data: any) -> any:
        if isinstance(data, dict):
            if "billing_interval" in data and "billing_frequency" not in data:
                data["billing_frequency"] = data["billing_interval"]
            elif "billing_frequency" in data and "billing_interval" not in data:
                data["billing_interval"] = data["billing_frequency"]
        return data

    @model_validator(mode="after")
    def validate_date_range(self) -> "SubscriptionPlanBase":
        if self.available_from and self.available_until:
            from_dt = self.available_from if isinstance(self.available_from, datetime) else datetime.combine(self.available_from, datetime.min.time())
            until_dt = self.available_until if isinstance(self.available_until, datetime) else datetime.combine(self.available_until, datetime.min.time())
            if from_dt > until_dt:
                raise ValueError("available_from cannot be after available_until")
        return self


class SubscriptionPlanCreate(SubscriptionPlanBase):
    products: Optional[List[PlanProductInput]] = Field(default_factory=list, description="Bundled products")


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    billing_frequency: Optional[BillingFrequency] = None
    minimum_quantity: Optional[int] = Field(None, ge=1)
    available_from: Optional[date | datetime] = None
    available_until: Optional[date | datetime] = None
    auto_close: Optional[bool] = None
    allow_early_cancellation: Optional[bool] = None
    allow_pause: Optional[bool] = None
    allow_renewal: Optional[bool] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Plan name cannot be empty or whitespace only")
            return stripped
        return v

    @model_validator(mode="before")
    @classmethod
    def sync_frequency_and_interval(cls, data: any) -> any:
        if isinstance(data, dict):
            if "billing_interval" in data and "billing_frequency" not in data:
                data["billing_frequency"] = data["billing_interval"]
            elif "billing_frequency" in data and "billing_interval" not in data:
                data["billing_interval"] = data["billing_frequency"]
        return data


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: str
    currency: str = "INR"
    billing_frequency: str
    minimum_quantity: int = 1
    available_from: Optional[str] = None
    available_until: Optional[str] = None
    auto_close: bool = True
    allow_early_cancellation: bool = True
    allow_pause: bool = True
    allow_renewal: bool = True
    is_active: bool = True
    products: List[PlanProductResponse] = Field(default_factory=list)

    @field_validator("price", mode="before")
    @classmethod
    def serialize_price(cls, v: Decimal | float | int | str | None) -> str:
        return format_decimal(v)

    @model_validator(mode="before")
    @classmethod
    def normalize_orm_data(cls, data: any) -> any:
        if hasattr(data, "__table__"):
            plan_prods = getattr(data, "plan_products", []) or []
            prods_list = [
                {"product_id": pp.product_id, "variant_id": pp.variant_id, "quantity": pp.quantity or 1}
                for pp in plan_prods
            ]
            
            avail_from = getattr(data, "available_from", None)
            avail_until = getattr(data, "available_until", None)

            def format_date_str(d: any) -> Optional[str]:
                if d is None:
                    return None
                if isinstance(d, datetime):
                    return d.strftime("%Y-%m-%d")
                if isinstance(d, date):
                    return d.isoformat()
                return str(d)

            def get_attr_or_default(attr: str, default: any) -> any:
                val = getattr(data, attr, default)
                return default if val is None else val

            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "description": getattr(data, "description", None),
                "price": getattr(data, "price"),
                "currency": get_attr_or_default("currency", "INR"),
                "billing_frequency": get_attr_or_default("billing_interval", "monthly"),
                "minimum_quantity": get_attr_or_default("minimum_quantity", 1),
                "available_from": format_date_str(avail_from),
                "available_until": format_date_str(avail_until),
                "auto_close": get_attr_or_default("auto_close", True),
                "allow_early_cancellation": get_attr_or_default("allow_early_cancellation", True),
                "allow_pause": get_attr_or_default("allow_pause", True),
                "allow_renewal": get_attr_or_default("allow_renewal", True),
                "is_active": get_attr_or_default("is_active", True),
                "products": prods_list,
            }
        elif isinstance(data, dict):
            if "billing_frequency" not in data and "billing_interval" in data:
                data["billing_frequency"] = data["billing_interval"]
        return data
