# Team Responsibilities and Handoffs

## Member 1 — Authentication
Owns registration, login, logout, password reset, user model, roles, authorization dependencies and staff account creation.

Handoff to all members:
- User/role schema.
- Auth dependency for protected endpoints.
- Agreed current-user representation.
- Login/session or token contract.
- How to enforce customer ownership.

## Member 2 — Products and Plans
Owns product CRUD, product variants, pricing rules, plans, plan-product association and related frontend screens.

Handoff to Member 3:
- Product and variant read APIs.
- Plan read API and plan-product details.
- Agreed price calculation rules.
- Stable IDs and response schemas.
- Whether a plan price is inclusive/exclusive of product lines and taxes.

## Member 3 — Quotations, Subscriptions, Billing and Payments
Owns quotation-to-subscription workflow, subscription lifecycle, billing schedule, invoice generation, payment records and idempotency.

Handoff to Member 4:
- Subscription and invoice summary endpoints.
- Billing run results.
- Payment status and outstanding balance definitions.

## Member 4 — Dashboard, Integration and Deployment Coordination
Owns dashboard pages, analytics presentation, frontend integration, shared navigation/layout and coordination of Docker/cloud deployment.

All members still own tests and documentation for their modules.

## Required team agreements
Before parallel coding, agree on:
1. Python and Node versions.
2. Naming conventions and API prefix.
3. Database naming and ID strategy.
4. Money representation and currency.
5. Authentication method.
6. Error response format.
7. Shared-file ownership.
8. Branch and PR rules.
9. Demo scope and deployment target.

## Daily check-in format
Each member posts:
- Done:
- Working on:
- Blocked by:
- Files/API changed:
- Help needed:
