# Team Status

Current progress and active tasks across all modules. Update this checklist when starting or completing tasks.

## Member 1 — Authentication & User Management (`auth`)
- [ ] User registration and password complexity validation
- [ ] Login and JWT authentication flow
- [ ] Role-based access control (Admin, Staff, Customer)
- [ ] Password reset flow
- [ ] User profile endpoints and frontend screens

## Member 2 — Products & Plans (`products`)
- [x] Product models, migrations, and CRUD API
- [x] Product variants and currency/pricing rules
- [x] Subscription plan creation and billing intervals (monthly/yearly)
- [x] Product catalog and plan management frontend screens

## Member 3 — Quotations, Subscriptions & Billing (`billing`)
- [ ] Quotation generation and approval workflow
- [ ] Subscription lifecycle management (Active, Paused, Canceled)
- [ ] Recurring invoice calculation and generation
- [ ] Tax calculations and payment simulation / recording
- [ ] Billing and invoice frontend screens

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
