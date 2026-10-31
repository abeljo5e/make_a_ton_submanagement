from typing import List, Dict
from pydantic import BaseModel, ConfigDict


class AnalyticsRevenuePoint(BaseModel):
    month: str
    revenue: str
    invoice_count: int


class AnalyticsRevenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: List[AnalyticsRevenuePoint]
    total_revenue: str
    currency: str = "INR"


class SubscriptionGrowthPoint(BaseModel):
    month: str
    new_subscriptions: int


class PlanPopularityItem(BaseModel):
    plan_name: str
    active_count: int


class AnalyticsSubscriptionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    growth: List[SubscriptionGrowthPoint]
    status_breakdown: Dict[str, int]
    plan_popularity: List[PlanPopularityItem]


class MonthlyInvoiceStat(BaseModel):
    month: str
    issued: int
    paid: int
    outstanding: int


class InvoiceTotals(BaseModel):
    paid_amount: str
    outstanding_amount: str
    cancelled_amount: str


class AnalyticsInvoicesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    monthly: List[MonthlyInvoiceStat]
    totals: InvoiceTotals
    payment_rate: str
