from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.plan import SubscriptionPlan


def _str_dec(value: Any) -> str:
    if value is None:
        return "0.00"
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


class AnalyticsService:
    @staticmethod
    def get_revenue_analytics(db: Session, months: int = 12) -> Dict[str, Any]:
        """Aggregate monthly revenue and transaction counts over the last N months."""
        months = min(max(months, 1), 24)
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        data = []
        total = Decimal("0.00")

        for i in range(months - 1, -1, -1):
            start = current_month_start - relativedelta(months=i)
            end = start + relativedelta(months=1)

            # Revenue from payments or paid invoices
            paid_inv_row = db.query(
                func.coalesce(func.sum(Invoice.amount_paid), 0).label("rev"),
                func.count(Invoice.id).label("cnt")
            ).filter(
                Invoice.created_at >= start,
                Invoice.created_at < end,
                Invoice.amount_paid > 0
            ).one()

            rev = Decimal(str(paid_inv_row.rev)).quantize(Decimal("0.01"))
            cnt = paid_inv_row.cnt

            if rev == 0:
                pay_row = db.query(
                    func.coalesce(func.sum(Payment.amount), 0).label("rev"),
                    func.count(Payment.id).label("cnt")
                ).filter(
                    Payment.payment_date >= start,
                    Payment.payment_date < end
                ).one()
                rev = Decimal(str(pay_row.rev)).quantize(Decimal("0.01"))
                cnt = pay_row.cnt

            total += rev
            data.append({
                "month": start.strftime("%Y-%m"),
                "revenue": str(rev),
                "invoice_count": cnt,
            })

        return {
            "data": data,
            "total_revenue": str(total),
            "currency": "INR",
        }

    @staticmethod
    def get_subscription_analytics(db: Session, months: int = 12) -> Dict[str, Any]:
        """Aggregate subscription growth and plan popularity trends."""
        months = min(max(months, 1), 24)
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        growth = []
        for i in range(months - 1, -1, -1):
            start = current_month_start - relativedelta(months=i)
            end = start + relativedelta(months=1)

            cnt = db.query(func.count(Subscription.id)).filter(
                Subscription.created_at >= start,
                Subscription.created_at < end
            ).scalar() or 0
            growth.append({
                "month": start.strftime("%Y-%m"),
                "new_subscriptions": cnt,
            })

        sub_rows = db.query(func.lower(Subscription.status), func.count(Subscription.id)).group_by(func.lower(Subscription.status)).all()
        status_breakdown = {r[0]: r[1] for r in sub_rows}

        popularity = []
        plans = db.query(SubscriptionPlan).all()
        for p in plans:
            active_cnt = db.query(func.count(Subscription.id)).filter(
                Subscription.plan_id == p.id,
                func.lower(Subscription.status) == "active"
            ).scalar() or 0
            popularity.append({
                "plan_name": p.name,
                "active_count": active_cnt,
            })
        popularity.sort(key=lambda x: x["active_count"], reverse=True)

        return {
            "growth": growth,
            "status_breakdown": status_breakdown,
            "plan_popularity": popularity,
        }

    @staticmethod
    def get_invoice_analytics(db: Session, months: int = 12) -> Dict[str, Any]:
        """Aggregate monthly invoice performance, balances, and collection rates."""
        months = min(max(months, 1), 24)
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly = []
        for i in range(months - 1, -1, -1):
            start = current_month_start - relativedelta(months=i)
            end = start + relativedelta(months=1)

            issued = db.query(func.count(Invoice.id)).filter(
                Invoice.created_at >= start,
                Invoice.created_at < end
            ).scalar() or 0

            paid = db.query(func.count(Invoice.id)).filter(
                Invoice.created_at >= start,
                Invoice.created_at < end,
                func.lower(Invoice.status) == "paid"
            ).scalar() or 0

            outstanding = db.query(func.count(Invoice.id)).filter(
                Invoice.created_at >= start,
                Invoice.created_at < end,
                func.lower(Invoice.status).in_(["draft", "confirmed"]),
                Invoice.balance_due > 0
            ).scalar() or 0

            monthly.append({
                "month": start.strftime("%Y-%m"),
                "issued": issued,
                "paid": paid,
                "outstanding": outstanding,
            })

        paid_amount = db.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).scalar() or Decimal("0.00")
        outstanding_amount = db.query(func.coalesce(func.sum(Invoice.balance_due), 0)).scalar() or Decimal("0.00")
        cancelled_amount = db.query(
            func.coalesce(func.sum(Invoice.total_amount), 0)
        ).filter(
            func.lower(Invoice.status) == "cancelled"
        ).scalar() or Decimal("0.00")

        total_non_cancelled = db.query(func.count(Invoice.id)).filter(
            func.lower(Invoice.status) != "cancelled"
        ).scalar() or 0

        total_paid = db.query(func.count(Invoice.id)).filter(
            func.lower(Invoice.status) == "paid"
        ).scalar() or 0

        payment_rate = (
            round((total_paid / total_non_cancelled) * 100, 1)
            if total_non_cancelled > 0 else 0.0
        )

        return {
            "monthly": monthly,
            "totals": {
                "paid_amount": _str_dec(paid_amount),
                "outstanding_amount": _str_dec(outstanding_amount),
                "cancelled_amount": _str_dec(cancelled_amount),
            },
            "payment_rate": str(payment_rate),
        }


analytics_service = AnalyticsService()
