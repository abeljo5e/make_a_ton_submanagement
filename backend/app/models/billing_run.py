"""
SQLAlchemy 2.0 model for Billing Runs.
Tracks automated and manual recurring billing executions, audit logs, and metrics.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class BillingRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "billing_runs"

    run_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="RUNNING", index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), default="SCHEDULED", nullable=False)  # SCHEDULED or MANUAL
    
    subscriptions_evaluated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invoices_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_invoiced_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
