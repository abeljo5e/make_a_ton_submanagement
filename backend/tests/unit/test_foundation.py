"""
Unit tests verifying Phase 1 foundation requirements:
- Decimal financial arithmetic vs floating-point risks
- Tax and discount calculations with ROUND_HALF_UP
- Recurrence calendar calculations and month-end drift
- Invoice payment settlement evaluation
"""
from datetime import datetime, timezone
from decimal import Decimal
import pytest

from app.core.calculations import (
    quantize_money,
    calculate_line_amounts,
    calculate_next_billing_date,
    calculate_billing_period,
    evaluate_invoice_payment_status,
)


class TestDecimalFinancialArithmetic:
    def test_float_inaccuracy_demonstration(self):
        """Show why float is strictly prohibited: 0.1 + 0.2 != 0.3 in binary float."""
        float_sum = 0.1 + 0.2
        assert float_sum != 0.3  # 0.30000000000000004
        
        # Decimal guarantees exact precision
        dec_sum = Decimal("0.1") + Decimal("0.2")
        assert dec_sum == Decimal("0.3")

    def test_quantize_money(self):
        assert quantize_money(Decimal("10.555")) == Decimal("10.56")  # ROUND_HALF_UP
        assert quantize_money(Decimal("10.554")) == Decimal("10.55")
        assert quantize_money(Decimal("10")) == Decimal("10.00")
        assert quantize_money("2500.5") == Decimal("2500.50")

    def test_calculate_line_amounts_standard(self):
        """
        Test line calculation:
        10 units @ 100.00 each = 1,000.00 subtotal
        10% discount = 100.00
        Taxable amount = 900.00
        18% tax (GST) = 162.00
        Total = 1,062.00
        """
        result = calculate_line_amounts(
            unit_price=Decimal("100.00"),
            quantity=10,
            discount_pct=Decimal("10.00"),
            tax_rate_pct=Decimal("18.00"),
        )
        assert result.subtotal == Decimal("1000.00")
        assert result.discount_amount == Decimal("100.00")
        assert result.taxable_amount == Decimal("900.00")
        assert result.tax_amount == Decimal("162.00")
        assert result.total_amount == Decimal("1062.00")

    def test_calculate_line_amounts_rounding(self):
        """
        Verify fractional tax rounds properly with ROUND_HALF_UP:
        1 unit @ 33.33 = 33.33 subtotal
        0% discount = 0.00
        5% tax = 1.6665 -> rounds to 1.67
        Total = 33.33 + 1.67 = 35.00
        """
        result = calculate_line_amounts(
            unit_price=Decimal("33.33"),
            quantity=1,
            discount_pct=Decimal("0.00"),
            tax_rate_pct=Decimal("5.00"),
        )
        assert result.subtotal == Decimal("33.33")
        assert result.tax_amount == Decimal("1.67")
        assert result.total_amount == Decimal("35.00")

    def test_invalid_line_inputs(self):
        with pytest.raises(ValueError, match="Quantity must be greater than zero"):
            calculate_line_amounts(Decimal("10.00"), 0)
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            calculate_line_amounts(Decimal("-5.00"), 1)
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100"):
            calculate_line_amounts(Decimal("10.00"), 1, discount_pct=Decimal("105.00"))


class TestRecurrenceAndBillingDates:
    def test_daily_recurrence(self):
        start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        next_date = calculate_next_billing_date(start, "daily")
        assert next_date == datetime(2026, 11, 2, 0, 0, 0, tzinfo=timezone.utc)

    def test_weekly_recurrence(self):
        start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        next_date = calculate_next_billing_date(start, "weekly")
        assert next_date == datetime(2026, 11, 8, 0, 0, 0, tzinfo=timezone.utc)

    def test_monthly_month_end_drift_safety(self):
        """
        Crucial requirement: Jan 31 + 1 month must end on Feb 28 (or 29 on leap year),
        never spill over into March.
        """
        # Non-leap year 2027
        jan31 = datetime(2027, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
        feb_date = calculate_next_billing_date(jan31, "monthly")
        assert feb_date == datetime(2027, 2, 28, 12, 0, 0, tzinfo=timezone.utc)

        # Leap year 2028
        jan31_leap = datetime(2028, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
        feb_leap = calculate_next_billing_date(jan31_leap, "monthly")
        assert feb_leap == datetime(2028, 2, 29, 12, 0, 0, tzinfo=timezone.utc)

    def test_yearly_recurrence(self):
        start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        next_date = calculate_next_billing_date(start, "yearly")
        assert next_date == datetime(2027, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    def test_unsupported_frequency(self):
        start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="Unsupported billing frequency"):
            calculate_next_billing_date(start, "biweekly")

    def test_calculate_billing_period(self):
        start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        period_start, period_end = calculate_billing_period(start, "monthly")
        assert period_start == start
        # Ends microsecond before next month
        assert period_end.month == 11
        assert period_end.day == 30
        assert period_end.hour == 23
        assert period_end.minute == 59
        assert period_end.second == 59


class TestPaymentStatusEvaluation:
    def test_no_payments(self):
        status = evaluate_invoice_payment_status(Decimal("1000.00"), Decimal("0.00"))
        assert status == "CONFIRMED"

    def test_partial_payment(self):
        status = evaluate_invoice_payment_status(Decimal("1000.00"), Decimal("500.00"))
        assert status == "PARTIALLY_PAID"

    def test_full_payment(self):
        status = evaluate_invoice_payment_status(Decimal("1000.00"), Decimal("1000.00"))
        assert status == "PAID"

    def test_overpayment(self):
        status = evaluate_invoice_payment_status(Decimal("1000.00"), Decimal("1200.00"))
        assert status == "PAID"
