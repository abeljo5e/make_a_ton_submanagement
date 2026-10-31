# Team Status

Current progress and active tasks across all modules. Update this checklist when starting or completing tasks.

## Member 1 — Authentication & User Management (`auth`)
- [ ] User registration and password complexity validation
- [ ] Login and JWT authentication flow
- [ ] Role-based access control (Admin, Staff, Customer)
- [ ] Password reset flow
- [ ] User profile endpoints and frontend screens

## Member 2 — Products & Plans (`products`)
- [ ] Product models, migrations, and CRUD API
- [ ] Product variants and currency/pricing rules
- [ ] Subscription plan creation and billing intervals (monthly/yearly)
- [ ] Product catalog and plan management frontend screens

## Member 3 — Quotations, Subscriptions & Billing (`billing`)
- [x] Phase 1: Architectural foundation, financial arithmetic, idempotency, and Member 2 schema review (`docs/MEMBER_3_FOUNDATION_SPEC.md`)
- [x] Phase 2: Database models, relationships, constraints, and Pydantic schemas (`Quotation`, `Subscription`, `Invoice`, `Payment`, `BillingRun`)
- [x] Phase 3: Quotation generation, line calculations, lifecycle states, and conversion workflow (`QuotationService`)
- [x] Phase 4: Subscription lifecycle management, pause/resume, cancel, and renewal (`SubscriptionService`)
- [x] Phase 5: Recurring billing runs, idempotent invoice generation, and payment reconciliation (`BillingService`, `PaymentService`)
- [x] Phase 6: REST API endpoints (`/quotations`, `/subscriptions`, `/invoices`, `/payments`, `/billing/run`)
- [ ] Phase 7: Billing and invoice frontend screens

## Member 4 — Dashboard, Analytics & Deployment (`dashboard`)
- [ ] Docker Compose setup for local development (FastAPI + PostgreSQL + Vite)
- [ ] Shared frontend shell, navigation, and API client
- [ ] Admin dashboard and KPI cards (MRR, active subscriptions, churn)
- [ ] Revenue analytics and subscription reporting charts
- [ ] End-to-end integration and smoke testing

## Current Issues
- Repository initialization completed; development branches to be created for parallel feature implementation.
