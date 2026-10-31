# Development Changelog

Every teammate (and their AI agent) adds an entry under the current date when completing a meaningful piece of work. Do not overwrite existing entries.

## 31 October 2026

### Team - Project Initialization
- Established project architecture and comprehensive technical documentation in `docs/` (requirements, database schema, API contracts, deployment, and coding standards).
- Added master AI agent instructions (`docs/BRIGHTLOOP_MASTER_AI_INSTRUCTIONS.md`).
- Added shared development coordination system: `CHANGELOG.md`, `TEAM_STATUS.md`, and `AI_CONTEXT.md`.

### Member 1 - Authentication & User Management (`auth`)
- [x] Initial documentation and specification for user roles, JWT authentication, and auth endpoints.
- [x] Implemented customer registration with strict password complexity validation (>8 chars, uppercase, lowercase, digit, special character).
- [x] Implemented bcrypt password hashing and PyJWT token generation and verification.
- [x] Implemented role-based access control (RBAC) with Admin, Staff, and Customer permission dependencies.
- [x] Implemented secure password reset flow with expiring single-use SHA-256 hashed tokens.
- [x] Implemented user profile endpoint, admin staff account creation (`POST /api/v1/staff`), user listing, and account activation/deactivation.
- [x] Built React frontend auth features: Login, Registration with live password meter, Forgot/Reset Password, Profile, and Admin User Management.
- [x] Added automated unit and integration tests (23 passing tests covering all auth & RBAC scenarios).

### Member 2 - Products & Plans (`products`)
- [x] Initial documentation for product CRUD, variant schemas, and subscription plan pricing models.
- [x] Implemented SQLAlchemy 2.0 ORM models for `Product`, `ProductVariant`, `SubscriptionPlan`, and `PlanProduct` (`plan_products`).
- [x] Implemented Pydantic v2 schemas and validation for products, variants, subscription plans, and bundled product associations.
- [x] Built `ProductService` and `PlanService` business layers enforcing Decimal money handling, foreign key referential integrity, and soft-deactivation.
- [x] Built FastAPI REST endpoints for `/api/v1/products`, `/api/v1/variants`, and `/api/v1/plans` adhering to `docs/API_CONTRACTS.md`.
- [x] Built React frontend with React Router:
  - Product management screens (list, create, edit, deactivate, and variant management).
  - Subscription plan management screens (list, create, edit, deactivate, and product bundling).
  - Customer-facing plan catalogue (`PlanCatalogue.jsx`) with billing frequency filtering.
- [x] Added automated unit and integration tests (11 passing tests across service and API layers).
- [x] Verified Vite production build (`dist/index.html`, `dist/assets/`).

### Member 3 - Billing & Subscriptions (`billing`)
- [x] Initial documentation for quotation workflows, subscription lifecycle, recurring invoice generation, and payment recording.
- [x] Phase 1 Foundation: Authored complete architectural and technical foundation specification (`docs/MEMBER_3_FOUNDATION_SPEC.md`) covering SQLAlchemy 2.x relationships, ACID transaction boundaries, financial decimal arithmetic (`ROUND_HALF_UP`), billing period recurrence algorithms, idempotency constraints (`uq_invoice_subscription_period`), and Member 2 catalog schema review.
- [x] Phase 1 Foundation Tests: Implemented core calculation engine (`backend/app/core/calculations.py`) and verified 15 unit tests covering float-safety, tax/discount rounding, calendar-aware month-end recurrence drift, and payment settlement logic.
- [x] Phase 2 Database Development: Created complete SQLAlchemy 2.x ORM models (`Quotation`, `QuotationLine`, `Subscription`, `SubscriptionLine`, `Invoice`, `InvoiceLine`, `Payment`, `BillingRun`) in `backend/app/models/` with `NUMERIC(12, 2)` monetary handling, UUID primary keys, and compound uniqueness constraint `uq_invoice_subscription_period`.
- [x] Phase 2 Schema & Validation: Authored matching Pydantic request/response schemas in `backend/app/schemas/`. Verified model relationships, conversion idempotency, and constraints with 26 automated unit tests in `backend/tests/unit/`.
- [x] Phase 3 Quotation Service: Implemented `QuotationService` supporting quotation creation, decimal line item math, `DRAFT` -> `SENT` -> `ACCEPTED`/`REJECTED`/`EXPIRED` lifecycle, and idempotent quotation-to-subscription conversion.
- [x] Phase 4 Subscription Service: Implemented `SubscriptionService` for active subscription creation, state transitions (`ACTIVE` <-> `PAUSED`, `CANCELED`, `EXPIRED`), cancellation reasons, and renewal billing date calculations.
- [x] Phase 5 Billing & Payment Services: Implemented `BillingService` for idempotent recurring invoice generation, batch `process_recurring_billing_run`, and `PaymentService` for partial/full payment settlement against invoices.
- [x] Phase 6 REST API Endpoints: Created FastAPI routers and endpoints for `/quotations`, `/subscriptions`, `/invoices`, `/payments`, and `/billing/run` with full CORS and dependency injection.
- [x] Verification: Built and verified 45 unit and end-to-end integration tests in `backend/tests/` validating the complete customer journey from quotation generation to payment settlement.
- [x] Phase 7 Frontend Development: Built complete React + Vite frontend client under `frontend/src/` featuring:
  - Quotation listing, dynamic multi-line creation form with real-time tax/discount math, and detail view with Send, Accept, Reject, and Convert actions.
  - Subscription management with status badges, lifecycle controls (Pause, Resume, Cancel with reason, Renew), and schedule tracking.
  - Invoice management with status filters (`CONFIRMED`, `PARTIALLY_PAID`, `PAID`), modal for recurring billing runs, line breakdowns, and payment recording interface.
  - Payment transaction history audit log with direct invoice navigation.
- [x] Phase 8 Verification & Build: Verified 45 backend tests in pytest and compiled a zero-warning, zero-error production build using Vite (`npm run build`).

### Member 4 - Dashboard & Integration (`dashboard`)
- [x] Initial documentation for repository layout, Docker Compose setup, and analytics integration.
- [ ] Initializing Docker Compose configuration, Vite frontend layout bootstrap, and API routing.
