"""
FastAPI application bootstrap for Brightloop Subscription Management System.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created in development/testing mode
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Brightloop Subscription Management System",
    description="REST API for authentication, product catalog, subscriptions, quotations, recurring billing, payments, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized validation error handler per docs/API_CONTRACTS.md
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {"msg": "Validation error"}
    error_msg = str(first_error.get("msg", "Invalid request parameters."))
    field_loc = " -> ".join([str(x) for x in first_error.get("loc", []) if x != "body"])
    detail_str = f"{field_loc}: {error_msg}" if field_loc else error_msg
    
    safe_errors = []
    for err in exc.errors():
        safe_err = {
            "type": err.get("type"),
            "loc": err.get("loc"),
            "msg": str(err.get("msg")),
        }
        safe_errors.append(safe_err)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": detail_str,
            "code": "VALIDATION_ERROR",
            "errors": safe_errors,
        },
    )


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "brightloop-backend", "env": settings.APP_ENV}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to Brightloop Subscription Management API",
        "docs": "/docs",
        "api_v1": "/api/v1",
    }
