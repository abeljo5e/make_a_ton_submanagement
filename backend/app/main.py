"""
FastAPI application bootstrap for Brightloop Subscription Management System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Brightloop Subscription Management System",
    description="REST API for subscriptions, quotations, recurring billing, and payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "brightloop-backend"}

