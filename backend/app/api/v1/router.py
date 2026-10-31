from fastapi import APIRouter
from backend.app.api.v1.endpoints.products import router as products_router
from backend.app.api.v1.endpoints.variants import router as variants_router
from backend.app.api.v1.endpoints.plans import router as plans_router

api_router = APIRouter()

# Register Member 2 endpoints
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(variants_router, prefix="/variants", tags=["Variants"])
api_router.include_router(plans_router, prefix="/plans", tags=["Plans"])
