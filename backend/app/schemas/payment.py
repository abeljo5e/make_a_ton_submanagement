"""
Pydantic schemas for Payments.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    invoice_id: uuid.UUID
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    currency: str = Field("INR", max_length=3)
    payment_method: str = Field("simulation", max_length=50)
    payment_reference: str = Field(..., max_length=100)
    payment_status: str = Field("SUCCESS", max_length=20)
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    payment_number: str
    invoice_id: uuid.UUID
    amount: Decimal
    currency: str
    payment_method: str
    payment_reference: str
    payment_status: str
    payment_date: datetime
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

