"""
API v1 Router aggregating endpoints for Brightloop Subscription Management System across all team modules.
"""
from fastapi import APIRouter

# Member 1: Auth & User Management
from app.api.v1.endpoints import auth, users

# Member 2: Products & Subscription Plans
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.variants import router as variants_router
from app.api.v1.endpoints.plans import router as plans_router

# Member 3: Quotations, Subscriptions, Invoices, Payments, Billing
from app.api.v1.endpoints.quotations import router as quotations_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.invoices import router as invoices_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.billing import router as billing_router

# Member 4: Dashboard & Analytics
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.analytics import router as analytics_router

api_router = APIRouter()

# Member 1 Routers
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Member 2 Routers
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(variants_router, prefix="/variants", tags=["Variants"])
api_router.include_router(plans_router, prefix="/plans", tags=["Plans"])

# Member 3 Routers
api_router.include_router(quotations_router)
api_router.include_router(subscriptions_router)
api_router.include_router(invoices_router)
api_router.include_router(payments_router)
api_router.include_router(billing_router)

# Member 4 Routers
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
