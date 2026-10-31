# Development Changelog

Every teammate (and their AI agent) adds an entry under the current date when completing a meaningful piece of work. Do not overwrite existing entries.

## 31 October 2026

### Team - Project Initialization
- Established project architecture and comprehensive technical documentation in `docs/` (requirements, database schema, API contracts, deployment, and coding standards).
- Added master AI agent instructions (`docs/BRIGHTLOOP_MASTER_AI_INSTRUCTIONS.md`).
- Added shared development coordination system: `CHANGELOG.md`, `TEAM_STATUS.md`, and `AI_CONTEXT.md`.

### Member 1 - Authentication & User Management (`auth`)
- [x] Initial documentation and specification for user roles, JWT authentication, and auth endpoints.
- [ ] Setting up user registration, login, JWT token authentication, and role authorization (Admin, Staff, Customer).

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
- [ ] Designing quotation generation, subscription lifecycle, recurring invoice generation, and payment records.

### Member 4 - Dashboard & Integration (`dashboard`)
- [x] Initial documentation for repository layout, Docker Compose setup, and analytics integration.
- [ ] Initializing Docker Compose configuration, Vite frontend layout bootstrap, and API routing.
