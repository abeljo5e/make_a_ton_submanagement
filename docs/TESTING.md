# Testing Strategy

## Test levels
1. Unit tests: isolated business rules and calculations.
2. API tests: endpoint validation, authorization and response contracts.
3. Integration tests: database relationships and transactions using a test database.
4. Frontend tests: key components, forms and user flows.
5. End-to-end smoke tests: critical workflow across frontend and backend.

## Backend
Use pytest and FastAPI TestClient/httpx. Tests must use a separate test database and never production data.

Minimum coverage:
- Registration validation and duplicate email.
- Role permissions and customer record isolation.
- Product/variant price calculations.
- Plan date and billing frequency validation.
- Tax and discount calculations.
- Subscription state transitions.
- Month-end/leap-year billing date calculations.
- Duplicate invoice prevention under retry.
- Partial/full payment reconciliation.
- Invoice snapshot immutability.

## Frontend
Test:
- Form validation.
- Loading, empty and error states.
- Protected routes and role-specific navigation.
- Product/plan create and edit flows.
- Invoice and payment display.

## Before a PR
Run relevant backend tests, frontend lint/build and the local Docker stack. Include commands and results in the PR description.

Do not claim tests passed unless you actually ran them.
