# Project Context

## Project
**Brightloop Software — Subscription Management System**
A centralized, multi-role subscription platform for managing products, product variants, pricing plans, quotations, customer subscriptions, recurring billing cycles, invoices, payments, and revenue analytics.

## Technology Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic
- **Frontend**: React, Vite, React Router, CSS
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **API Style**: REST / JSON with standard HTTP status codes

## Architecture
- **Client-Server Communication**: The React SPA communicates with the FastAPI backend over RESTful HTTPS endpoints with JSON payloads.
- **Layered Backend**:
  `Router (app/api/v1/)` -> `Auth Dependency (app/core/security.py)` -> `Service (app/services/)` -> `SQLAlchemy ORM (app/models/)` -> `PostgreSQL`
  - Routes stay thin; business logic resides strictly in reusable services.
  - Data transfer and validation are handled by Pydantic schemas (`app/schemas/`).
- **Database & Money Handling**:
  - Always use `NUMERIC` in PostgreSQL and `Decimal` in Python for monetary calculations (never floating-point).
  - Store all timestamps in UTC.
  - Multi-step database operations must run inside atomic transactions.
- **Billing Worker**: A background worker handles scheduled recurring billing runs by invoking the same shared billing service methods.

## Important Rules
1. **Mandatory Context Check**: No AI agent should blindly modify code before reading the latest project context (`AI_CONTEXT.md`, `TEAM_STATUS.md`, and `CHANGELOG.md`).
2. **Module Boundaries**: Do not modify another team member's module without coordinating first.
3. **API Contracts**: Do not change existing API interfaces or response shapes without informing the team.
4. **Secrets & Security**: Never commit passwords, `.env` files, API keys, or raw payment card details. Enforce backend RBAC and password hashing.
5. **No Destructive Log Edits**: Never overwrite or delete existing changelog entries. Always append new work under the appropriate date.

## Current Architecture
```text
brightloop/
├── frontend/                 # React + Vite application
│   └── src/
│       ├── app/              # Router and application bootstrap
│       ├── components/       # Shared reusable UI elements
│       ├── features/         # Feature modules (auth, products, billing, dashboard)
│       └── lib/api.js        # Central API client
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/           # API routes and endpoints
│   │   ├── core/             # Configuration, JWT auth, security utilities
│   │   ├── db/               # Database engine and session management
│   │   ├── models/           # SQLAlchemy 2.x ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Core business logic
│   │   └── workers/          # Background/scheduled billing workers
│   └── alembic/              # Database migration scripts
├── docs/                     # Specifications, contracts, schema diagrams
├── CHANGELOG.md              # Historical log of completed features
├── TEAM_STATUS.md            # Active tasks and module progress
├── AI_CONTEXT.md             # Shared AI instructions and system context
└── docker-compose.yml        # Development environment configuration
```

### Shared Files Coordination
Coordinate before making modifications to shared infrastructure files:
- `backend/app/main.py`
- `backend/app/db/*`
- `backend/app/core/config.py`
- `backend/app/api/v1/router.py`
- `frontend/src/app/*`
- `frontend/src/lib/api.js`
- `docker-compose.yml`

## AI Agent Workflow & Instructions

This repository uses a lightweight shared memory system for teammates and AI coding agents.

### When Starting an AI Session
Instruct your agent:
> *"First read `AI_CONTEXT.md`, `TEAM_STATUS.md`, and the latest entries in `CHANGELOG.md`. Understand the existing project structure and recent changes before modifying anything."*

### After Completing a Task
Instruct your agent:
> *"Update `CHANGELOG.md` with your completed changes, update `TEAM_STATUS.md` if necessary, and mention any modified interfaces, dependencies, or unresolved issues. Do not overwrite existing changelog entries."*
