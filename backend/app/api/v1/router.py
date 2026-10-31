from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# Member 1: Authentication and User Management
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Member 2 (Products/Plans), Member 3 (Billing/Subscriptions),
# and Member 4 (Dashboard) will register their routers here upon implementation.
