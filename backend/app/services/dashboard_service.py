import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User, Customer, UserRole
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.payment import Payment


def _str_dec(value: Optional[Decimal]) -> str:
    """Format Decimal value as a 2-decimal place string."""
    if value is None:
        return "0.00"
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


class DashboardService:
    @staticmethod
    def get_summary(db: Session) -> Dict[str, Any]:
        """Return high-level KPI snapshot."""
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_customers = db.query(func.count(Customer.id)).scalar() or 0
        if total_customers == 0:
            total_customers = db.query(func.count(User.id)).filter(
                (User.role == UserRole.CUSTOMER) | (User.role == "customer")
            ).scalar() or 0

        # Subscriptions by status
        sub_rows = db.query(func.lower(Subscription.status), func.count(Subscription.id)).group_by(func.lower(Subscription.status)).all()
        sub_counts = {row[0]: row[1] for row in sub_rows}

        active_subs = sub_counts.get("active", 0)
        paused_subs = sub_counts.get("paused", 0)
        cancelled_subs = sub_counts.get("closed", 0) + sub_counts.get("cancelled", 0) + sub_counts.get("canceled", 0)

        # Invoices
        total_invoices = db.query(func.count(Invoice.id)).scalar() or 0
        outstanding_count = db.query(func.count(Invoice.id)).filter(
            func.lower(Invoice.status).in_(["draft", "confirmed"]),
            Invoice.balance_due > 0
        ).scalar() or 0

        # Total revenue: sum of amount_paid across all invoices
        revenue = db.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).scalar()
        if not revenue or revenue == 0:
            revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or Decimal("0.00")

        return {
            "users": total_users,
            "customers": total_customers,
            "active_subscriptions": active_subs,
            "paused_subscriptions": paused_subs,
            "cancelled_subscriptions": cancelled_subs,
            "total_invoices": total_invoices,
            "outstanding_invoices": outstanding_count,
            "revenue_total": _str_dec(revenue),
        }

    @staticmethod
    def get_revenue_series(db: Session, months: int = 12) -> List[Dict[str, str]]:
        """Return monthly revenue series for the last N months."""
        months = min(max(months, 1), 24)
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        series = []
        for i in range(months - 1, -1, -1):
            start = current_month_start - relativedelta(months=i)
            end = start + relativedelta(months=1)
            
            # Revenue from payments or invoices in this month window
            rev = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
                Payment.payment_date >= start,
                Payment.payment_date < end
            ).scalar()

            if not rev or rev == 0:
                rev = db.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).filter(
                    Invoice.created_at >= start,
                    Invoice.created_at < end,
                    Invoice.amount_paid > 0
                ).scalar() or Decimal("0.00")

            series.append({
                "month": start.strftime("%Y-%m"),
                "revenue": _str_dec(rev),
            })
        return series

    @staticmethod
    def get_subscriptions_metrics(db: Session) -> Dict[str, Any]:
        """Return subscription breakdown by status, plan, and 10 recent subscriptions."""
        sub_rows = db.query(func.lower(Subscription.status), func.count(Subscription.id)).group_by(func.lower(Subscription.status)).all()
        by_status = {row[0]: row[1] for row in sub_rows}

        # Breakdown by plan
        plan_counts: List[Dict[str, Any]] = []
        plans = db.query(SubscriptionPlan).all()
        for p in plans:
            cnt = db.query(func.count(Subscription.id)).filter(
                Subscription.plan_id == p.id,
                func.lower(Subscription.status) == "active"
            ).scalar() or 0
            plan_counts.append({"plan_name": p.name, "count": cnt})

        # 10 recent subscriptions
        recent_subs = db.query(Subscription).order_by(Subscription.created_at.desc()).limit(10).all()
        recent_list = []
        for s in recent_subs:
            cust_name = "Customer"
            cust = db.query(Customer).filter(Customer.id == s.customer_id).first()
            if cust and cust.user:
                cust_name = cust.user.full_name
            else:
                user = db.query(User).filter(User.id == s.customer_id).first()
                if user:
                    cust_name = user.full_name

            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == s.plan_id).first() if s.plan_id else None
            plan_title = plan.name if plan else (f"Plan {str(s.plan_id)[:8]}" if s.plan_id else "Standard Plan")

            recent_list.append({
                "id": str(s.id),
                "customer_name": cust_name,
                "plan_name": plan_title,
                "status": str(s.status).lower(),
                "start_date": s.start_date.isoformat() if s.start_date else None,
            })

        return {
            "by_status": by_status,
            "by_plan": plan_counts,
            "recent": recent_list,
        }

    @staticmethod
    def get_invoices_metrics(db: Session) -> Dict[str, Any]:
        """Return invoice metrics and status breakdown."""
        status_rows = db.query(func.lower(Invoice.status), func.count(Invoice.id)).group_by(func.lower(Invoice.status)).all()
        by_status = {row[0]: row[1] for row in status_rows}

        outstanding = db.query(
            func.coalesce(func.sum(Invoice.balance_due), 0)
        ).filter(
            func.lower(Invoice.status).in_(["draft", "confirmed"])
        ).scalar() or Decimal("0.00")

        paid = db.query(
            func.coalesce(func.sum(Invoice.amount_paid), 0)
        ).scalar() or Decimal("0.00")

        recent_invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(10).all()
        recent_list = []
        for inv in recent_invoices:
            cust_name = "Customer"
            cust = db.query(Customer).filter(Customer.id == inv.customer_id).first()
            if cust and cust.user:
                cust_name = cust.user.full_name
            else:
                user = db.query(User).filter(User.id == inv.customer_id).first()
                if user:
                    cust_name = user.full_name

            recent_list.append({
                "id": str(inv.id),
                "customer_name": cust_name,
                "amount": _str_dec(inv.total_amount),
                "status": str(inv.status).lower(),
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
            })

        return {
            "by_status": by_status,
            "outstanding_amount": _str_dec(outstanding),
            "paid_amount": _str_dec(paid),
            "recent": recent_list,
        }

    @staticmethod
    def get_customer_dashboard(db: Session, customer_id: uuid.UUID) -> Dict[str, Any]:
        """Return customer's active subscription, recent invoices, and available plans."""
        sub = db.query(Subscription).filter(
            (Subscription.customer_id == customer_id),
            func.lower(Subscription.status).in_(["active", "paused"])
        ).order_by(Subscription.created_at.desc()).first()

        subscription_data = None
        if sub:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first() if sub.plan_id else None
            plan_title = plan.name if plan else "Standard Plan"
            subscription_data = {
                "id": str(sub.id),
                "plan_name": plan_title,
                "status": str(sub.status).lower(),
                "next_billing": sub.next_billing_date.isoformat() if sub.next_billing_date else None,
                "start_date": sub.start_date.isoformat() if sub.start_date else None,
            }

        inv_rows = db.query(Invoice).filter(
            Invoice.customer_id == customer_id
        ).order_by(Invoice.created_at.desc()).limit(5).all()

        recent_invoices = [
            {
                "id": str(inv.id),
                "amount": _str_dec(inv.total_amount),
                "status": str(inv.status).lower(),
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
            }
            for inv in inv_rows
        ]

        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active.is_(True)).all()
        available_plans = [
            {
                "id": str(p.id),
                "name": p.name,
                "price": _str_dec(p.price),
                "billing_frequency": p.billing_interval,
            }
            for p in plans
        ]

        return {
            "subscription": subscription_data,
            "recent_invoices": recent_invoices,
            "available_plans": available_plans,
        }


dashboard_service = DashboardService()
