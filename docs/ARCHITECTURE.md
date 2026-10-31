# System Architecture

## High-level components
```text
Browser
  |
  v
React SPA (Vite)
  | HTTPS / JSON
  v
FastAPI application
  |-- Authentication and authorization
  |-- Product and plan services
  |-- Quotation and subscription services
  |-- Billing and payment services
  |-- Analytics services
  |
  v
SQLAlchemy 2.x
  |
  v
PostgreSQL

Scheduled billing worker/job ---> shared billing service ---> PostgreSQL
```

## Architectural rules
- React is responsible for presentation and client-side interaction, not authoritative business rules.
- FastAPI owns validation, authorization and business logic.
- SQLAlchemy models represent persistence. Pydantic schemas define request/response contracts.
- Services contain reusable business operations; route handlers remain thin.
- Alembic owns schema migrations.
- Scheduled billing and manual billing triggers call the same service function.
- Monetary values use `NUMERIC`/`Decimal`.
- Store timestamps consistently in UTC; display in the user's locale.
- Use database transactions for multi-step operations.
- Do not expose SQLAlchemy models directly as API responses.

## Backend layering
`router -> dependency/auth -> service -> repository/SQLAlchemy -> PostgreSQL`

A repository layer is optional for this project; do not add abstraction without a clear benefit. Keep business rules in services.

## Frontend layering
`page -> reusable components/hooks -> service/API client -> FastAPI`

## Deployment shape
The frontend and backend can be deployed as separate services. PostgreSQL must be a managed or persistent database service. Never rely on a container's temporary filesystem for database persistence.
