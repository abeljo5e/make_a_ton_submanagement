# Team Status

Current progress and active tasks across all modules. Update this checklist when starting or completing tasks.

## Member 1 — Authentication & User Management (`auth`)
- [x] User registration and password complexity validation
- [x] Login and JWT authentication flow
- [x] Role-based access control (Admin, Staff, Customer)
- [x] Password reset flow
- [x] User profile endpoints and frontend screens

## Member 2 — Products & Plans (`products`)
- [x] Product models, migrations, and CRUD API
- [x] Product variants and currency/pricing rules
- [x] Subscription plan creation and billing intervals (monthly/yearly)
- [x] Product catalog and plan management frontend screens

## Member 3 — Quotations, Subscriptions & Billing (`billing`)
- [x] Phase 1: Architectural foundation, financial arithmetic, idempotency, and Member 2 schema review (`docs/MEMBER_3_FOUNDATION_SPEC.md`)
- [x] Phase 2: Database models, relationships, constraints, and Pydantic schemas (`Quotation`, `Subscription`, `Invoice`, `Payment`, `BillingRun`)
- [x] Phase 3: Quotation generation, line calculations, lifecycle states, and conversion workflow (`QuotationService`)
- [x] Phase 4: Subscription lifecycle management, pause/resume, cancel, and renewal (`SubscriptionService`)
- [x] Phase 5: Recurring billing runs, idempotent invoice generation, and payment reconciliation (`BillingService`, `PaymentService`)
- [x] Phase 6: REST API endpoints (`/quotations`, `/subscriptions`, `/invoices`, `/payments`, `/billing/run`)
- [x] Phase 7: Billing, quotation, subscription, and invoice frontend UI screens (`frontend/src/features/`)
- [x] Phase 8: Full verification (45 automated backend tests + Vite frontend production build passing with 0 errors)

## Member 4 — Dashboard, Analytics & Deployment (`dashboard`)
- [ ] Docker Compose setup for local development (FastAPI + PostgreSQL + Vite)
- [ ] Shared frontend shell, navigation, and API client
- [ ] Admin dashboard and KPI cards (MRR, active subscriptions, churn)
- [ ] Revenue analytics and subscription reporting charts
- [ ] End-to-end integration and smoke testing

## Current Issues
- Member 2's module (Products and Subscription Plans) backend and frontend components are implemented and tested (11 passing tests, Vite production build verified).
- Integration handoff ready for Member 3 (`billing`) to consume product and plan APIs for quotations/subscriptions.
- Awaiting Member 1 (`auth`) to supply JWT authorization middleware to replace the temporary mock role provider in `App.jsx`.
