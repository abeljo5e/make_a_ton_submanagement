"""
Pydantic schemas for Billing Runs.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class BillingRunRequest(BaseModel):
    run_date: Optional[datetime] = None


class BillingRunResponse(BaseModel):
    id: uuid.UUID
    run_date: datetime
    status: str
    trigger_type: str
    subscriptions_evaluated: int
    invoices_generated: int
    total_invoiced_amount: Decimal
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
