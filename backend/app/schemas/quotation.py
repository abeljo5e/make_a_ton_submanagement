"""
Pydantic schemas for Quotations and Quotation Lines.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class QuotationLineBase(BaseModel):
    description: str = Field(..., max_length=255)
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(..., ge=Decimal("0.00"))
    discount_pct: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"), le=Decimal("100.00"))
    tax_rate_pct: Decimal = Field(Decimal("0.00"), ge=Decimal("0.00"))
    plan_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    variant_id: Optional[uuid.UUID] = None


class QuotationLineCreate(QuotationLineBase):
    pass


class QuotationLineResponse(QuotationLineBase):
    id: uuid.UUID
    quotation_id: uuid.UUID
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuotationCreate(BaseModel):
    customer_id: uuid.UUID
    currency: str = Field("INR", max_length=3)
    valid_until: Optional[datetime] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    lines: List[QuotationLineCreate] = Field(..., min_length=1)


class QuotationUpdate(BaseModel):
    status: Optional[str] = None
    valid_until: Optional[datetime] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None


class QuotationResponse(BaseModel):
    id: uuid.UUID
    quotation_number: str
    customer_id: uuid.UUID
    status: str
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    valid_until: Optional[datetime] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    lines: List[QuotationLineResponse] = []

    model_config = ConfigDict(from_attributes=True)
