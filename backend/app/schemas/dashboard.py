from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    users: int
    customers: int
    active_subscriptions: int
    paused_subscriptions: int
    cancelled_subscriptions: int
    total_invoices: int
    outstanding_invoices: int
    revenue_total: Optional[str] = "0.00"


class RevenuePoint(BaseModel):
    month: str
    revenue: str


class DashboardRevenueResponse(BaseModel):
    data: List[RevenuePoint]


class RecentSubscriptionItem(BaseModel):
    id: str
    customer_name: str
    plan_name: str
    status: str
    start_date: Optional[str] = None


class PlanSubscriptionCount(BaseModel):
    plan_name: str
    count: int


class DashboardSubscriptionsResponse(BaseModel):
    by_status: Dict[str, int]
    by_plan: List[Dict[str, Any]]
    recent: List[RecentSubscriptionItem]


class RecentInvoiceItem(BaseModel):
    id: str
    customer_name: str
    amount: str
    status: str
    due_date: Optional[str] = None


class DashboardInvoicesResponse(BaseModel):
    by_status: Dict[str, int]
    outstanding_amount: str
    paid_amount: str
    recent: List[RecentInvoiceItem]


class CustomerSubscriptionInfo(BaseModel):
    id: str
    plan_name: str
    status: str
    next_billing: Optional[str] = None
    start_date: Optional[str] = None


class CustomerInvoiceItem(BaseModel):
    id: str
    amount: str
    status: str
    due_date: Optional[str] = None


class AvailablePlanItem(BaseModel):
    id: str
    name: str
    price: str
    billing_frequency: str


class CustomerDashboardResponse(BaseModel):
    subscription: Optional[CustomerSubscriptionInfo] = None
    recent_invoices: List[CustomerInvoiceItem] = []
    available_plans: List[AvailablePlanItem] = []
