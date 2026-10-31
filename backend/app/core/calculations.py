"""
Financial and billing calculation utilities for Member 3 (Quotations, Subscriptions & Billing).
Enforces zero floating-point arithmetic, using Python Decimal with explicit ROUND_HALF_UP.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple
from dateutil.relativedelta import relativedelta

TWOPLACES = Decimal("0.01")


def quantize_money(amount: Decimal) -> Decimal:
    """Quantize any decimal value to two decimal places using ROUND_HALF_UP."""
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class LineCalculationResult:
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal


def calculate_line_amounts(
    unit_price: Decimal,
    quantity: int,
    discount_pct: Decimal = Decimal("0.00"),
    tax_rate_pct: Decimal = Decimal("0.00"),
) -> LineCalculationResult:
    """
    Calculate financial line amounts strictly with Decimal arithmetic.
    
    Subtotal = unit_price * quantity
    Discount = Subtotal * (discount_pct / 100)
    Taxable = Subtotal - Discount
    Tax = Taxable * (tax_rate_pct / 100)
    Total = Taxable + Tax
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")
    if unit_price < Decimal("0.00"):
        raise ValueError("Unit price cannot be negative")
    if discount_pct < Decimal("0.00") or discount_pct > Decimal("100.00"):
        raise ValueError("Discount percentage must be between 0 and 100")
    if tax_rate_pct < Decimal("0.00"):
        raise ValueError("Tax rate percentage cannot be negative")

    q_unit_price = quantize_money(unit_price)
    subtotal = quantize_money(q_unit_price * Decimal(quantity))
    
    # Calculate discount
    raw_discount = subtotal * (Decimal(str(discount_pct)) / Decimal("100.00"))
    discount_amount = quantize_money(raw_discount)
    
    taxable_amount = quantize_money(subtotal - discount_amount)
    
    # Calculate tax
    raw_tax = taxable_amount * (Decimal(str(tax_rate_pct)) / Decimal("100.00"))
    tax_amount = quantize_money(raw_tax)
    
    total_amount = quantize_money(taxable_amount + tax_amount)
    
    return LineCalculationResult(
        subtotal=subtotal,
        discount_amount=discount_amount,
        taxable_amount=taxable_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
    )


def calculate_next_billing_date(current_date: datetime, frequency: str) -> datetime:
    """
    Compute next recurring billing date using calendar-aware relativedelta.
    Accurately handles month-ends (e.g. Jan 31 -> Feb 28/29).
    """
    freq = frequency.lower()
    if freq == "daily":
        return current_date + relativedelta(days=1)
    elif freq == "weekly":
        return current_date + relativedelta(weeks=1)
    elif freq == "monthly":
        return current_date + relativedelta(months=1)
    elif freq == "yearly":
        return current_date + relativedelta(years=1)
    else:
        raise ValueError(f"Unsupported billing frequency: '{frequency}'")


def calculate_billing_period(start_date: datetime, frequency: str) -> Tuple[datetime, datetime]:
    """
    Calculate the start and end timestamps of a billing period.
    The period end is right before the next billing date.
    """
    next_date = calculate_next_billing_date(start_date, frequency)
    # The billing period ends 1 microsecond before the next billing date
    period_end = next_date - relativedelta(microseconds=1)
    return start_date, period_end


def evaluate_invoice_payment_status(total_amount: Decimal, total_paid: Decimal) -> str:
    """Determine the invoice status based on total invoice amount and total payments recorded."""
    q_total = quantize_money(total_amount)
    q_paid = quantize_money(total_paid)
    
    if q_paid <= Decimal("0.00"):
        return "CONFIRMED"
    elif q_paid < q_total:
        return "PARTIALLY_PAID"
    else:
        return "PAID"
