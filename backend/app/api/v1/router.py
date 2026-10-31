"""
API v1 Router aggregating endpoints for Brightloop Subscription Management System.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.quotations import router as quotations_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.invoices import router as invoices_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.billing import router as billing_router

api_router = APIRouter()
api_router.include_router(quotations_router)
api_router.include_router(subscriptions_router)
api_router.include_router(invoices_router)
api_router.include_router(payments_router)
api_router.include_router(billing_router)

