import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def format_decimal(v: Decimal | float | int | str | None) -> str:
    if v is None:
        return "0.00"
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return f"{Decimal(str(v)):.2f}"


# --- Product Variant Schemas ---

class ProductVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Variant name")
    description: Optional[str] = Field(None, description="Variant description")
    additional_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Additional price for this variant"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Variant name cannot be empty or whitespace only")
        return stripped


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    additional_price: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Variant name cannot be empty or whitespace only")
            return stripped
        return v


class ProductVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    additional_price: str
    is_active: bool = True

    @field_validator("additional_price", mode="before")
    @classmethod
    def serialize_additional_price(cls, v: Decimal | float | int | str | None) -> str:
        return format_decimal(v)


# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed product description")
    category: Optional[str] = Field(None, max_length=100, description="Product category or type")
    type: Optional[str] = Field(None, max_length=100, description="Alias for category / product type")
    sales_price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        description="Base sales price of the product"
    )
    cost_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        description="Cost price of the product"
    )
    currency: str = Field(default="INR", min_length=3, max_length=3, description="ISO 4217 Currency code")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Product name cannot be empty or whitespace only")
        return stripped

    @model_validator(mode="before")
    @classmethod
    def sync_type_and_category(cls, data: any) -> any:
        if isinstance(data, dict):
            # Normalize type and category interchangeably
            if "type" in data and not data.get("category"):
                data["category"] = data["type"]
            elif "category" in data and not data.get("type"):
                data["type"] = data["category"]
        return data


class ProductCreate(ProductBase):
    variants: Optional[List[ProductVariantCreate]] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=100)
    sales_price: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    cost_price: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Product name cannot be empty or whitespace only")
            return stripped
        return v

    @model_validator(mode="before")
    @classmethod
    def sync_type_and_category(cls, data: any) -> any:
        if isinstance(data, dict):
            if "type" in data and not data.get("category"):
                data["category"] = data["type"]
            elif "category" in data and not data.get("type"):
                data["type"] = data["category"]
        return data


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    sales_price: str
    cost_price: str
    currency: str
    status: str
    variants: List[ProductVariantResponse] = Field(default_factory=list)

    @field_validator("sales_price", "cost_price", mode="before")
    @classmethod
    def serialize_price(cls, v: Decimal | float | int | str | None) -> str:
        return format_decimal(v)

    @model_validator(mode="before")
    @classmethod
    def populate_virtual_fields(cls, data: any) -> any:
        # If input is an ORM object or dict
        if hasattr(data, "is_active") and not hasattr(data, "status"):
            status_val = "active" if getattr(data, "is_active") else "inactive"
            category_val = getattr(data, "category", None)
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "description": getattr(data, "description", None),
                "type": category_val,
                "sales_price": getattr(data, "sales_price"),
                "cost_price": getattr(data, "cost_price"),
                "currency": getattr(data, "currency"),
                "status": status_val,
                "variants": getattr(data, "variants", []),
            }
        elif isinstance(data, dict):
            if "status" not in data and "is_active" in data:
                data["status"] = "active" if data["is_active"] else "inactive"
            if "type" not in data and "category" in data:
                data["type"] = data["category"]
        return data
