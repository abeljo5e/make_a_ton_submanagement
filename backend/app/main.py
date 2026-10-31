from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import api_router
from backend.app.db.base import Base
from backend.app.db.session import engine

# Automatically create tables for local development if not using migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Brightloop Subscription Management API",
    description="API for managing products, plans, quotations, subscriptions, and invoices.",
    version="1.0.0",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 router under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Brightloop API"}
