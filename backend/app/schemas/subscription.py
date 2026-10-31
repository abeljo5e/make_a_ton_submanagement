"""
Pydantic schemas for Subscriptions and Subscription Lines.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class SubscriptionLineBase(BaseModel):
    description: str = Field(..., max_length=255)
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(..., ge=Decimal("0.00"))
    discount_pct: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"), le=Decimal("100.00"))
    tax_rate_pct: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    product_id: Optional[uuid.UUID] = None
    variant_id: Optional[uuid.UUID] = None


class SubscriptionLineCreate(SubscriptionLineBase):
    pass


class SubscriptionLineResponse(SubscriptionLineBase):
    id: uuid.UUID
    subscription_id: uuid.UUID
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    customer_id: uuid.UUID
    plan_id: uuid.UUID
    quotation_id: Optional[uuid.UUID] = None
    billing_frequency: str = Field("monthly", pattern="^(daily|weekly|monthly|yearly)$")
    currency: str = Field("INR", max_length=3)
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    lines: List[SubscriptionLineCreate] = Field(..., min_length=1)


class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    auto_renew: Optional[bool] = None
    end_date: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    subscription_number: str
    customer_id: uuid.UUID
    plan_id: uuid.UUID
    quotation_id: Optional[uuid.UUID] = None
    status: str
    billing_frequency: str
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    start_date: datetime
    next_billing_date: datetime
    end_date: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    auto_renew: bool
    created_at: datetime
    updated_at: datetime
    lines: List[SubscriptionLineResponse] = []

    model_config = ConfigDict(from_attributes=True)

