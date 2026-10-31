# MEMBER 1 — AUTHENTICATION AND USER MANAGEMENT
## Brightloop Subscription Management System

### 1. Objective

Build the complete authentication and user-management system. This module controls who can access the application and what actions each user is permitted to perform.

### 2. Responsibilities

- Customer registration
- User login and logout
- Password hashing
- Password complexity validation
- Role-based access control
- Admin-only staff account creation
- User profile management
- Password reset through email
- Protected frontend routes
- Backend authorization

### 3. Development roadmap

#### Phase 1 — Understand the foundation
1. Read the project requirements and architecture.
2. Understand FastAPI, SQLAlchemy and Pydantic.
3. Understand HTTP requests, responses and REST APIs.
4. Understand password hashing and authentication.
5. Review the agreed database schema and API contracts.

#### Phase 2 — Database development

Create and manage:

**users**
- id
- full_name
- email
- password_hash
- role
- is_active
- created_at
- updated_at

Add any additional fields required by the approved schema.

Implement appropriate uniqueness constraints and relationships.

#### Phase 3 — Backend development

Implement these endpoints, adjusting names to the team's API contract:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Customer registration |
| POST | /api/auth/login | User login |
| POST | /api/auth/logout | Logout/session handling |
| GET | /api/auth/me | Current user details |
| POST | /api/auth/forgot-password | Request password reset |
| POST | /api/auth/reset-password | Reset password |
| GET | /api/users | List users |
| POST | /api/users/staff | Admin creates staff |
| GET | /api/users/{id} | View user |
| PUT | /api/users/{id} | Update user |
| PATCH | /api/users/{id}/status | Activate/deactivate user |

Implement secure authentication using an agreed token or session strategy.

Important:
- Never store plain-text passwords.
- Never allow public registration to create an admin account.
- Validate permissions on the backend, not just in the frontend.
- Do not expose password hashes through API responses.
- Implement safe password-reset tokens with expiration.

#### Phase 4 — Frontend development

Build:
1. Login page.
2. Customer registration page.
3. Forgot-password page.
4. Reset-password page.
5. User profile page.
6. Admin user-management page.
7. Staff account creation form.

Implement:
- Form validation
- Error messages
- Loading states
- Protected routes
- Role-based navigation

#### Phase 5 — Testing

Test:
- Valid and invalid login.
- Duplicate email registration.
- Weak password rejection.
- Unauthorized admin access.
- Customer attempting staff-only operations.
- Invalid or expired reset tokens.
- Inactive account login.
- Accessing protected pages without authentication.

### 4. Dependencies

Needs:
- Agreed user and role schema.
- Backend project structure.
- Frontend routing conventions.
- Email configuration for password reset.

Provides:
- Authentication APIs.
- Current-user information.
- Role and permission checks for all other modules.

### 5. Final deliverables

- Working authentication system.
- User-management functionality.
- Secure role-based authorization.
- Login and registration interfaces.
- Password reset functionality.
- Automated tests.
- API documentation.

### 6. Definition of completion

The module is complete when users can securely register and log in, admins can manage staff, and all protected operations enforce the correct permissions.





# MEMBER 2 — PRODUCTS AND SUBSCRIPTION PLANS
## Brightloop Subscription Management System

### 1. Objective

Build the product catalogue and subscription-plan management system.

This module defines what Brightloop sells, how products are organized, and which subscription plans customers can purchase.

### 2. Responsibilities

- Product management
- Product variants
- Product pricing
- Product descriptions
- Subscription plan management
- Billing intervals
- Product-plan relationships
- Plan availability
- Customer-facing plan catalogue

### 3. Development roadmap

#### Phase 1 — Understand the foundation

Learn and understand:
- FastAPI CRUD operations
- SQLAlchemy models and relationships
- Pydantic validation
- PostgreSQL foreign keys
- React forms and API integration
- REST API conventions

Review the agreed database schema and API contracts before creating models.

#### Phase 2 — Database development

Create and manage these entities:

**products**
- id
- name
- description
- category
- is_active
- created_at

**product_variants**
- id
- product_id
- name
- description
- price
- is_active

**subscription_plans**
- id
- name
- description
- price
- billing_interval
- billing_interval_count
- is_active
- created_at

**plan_products**
- id
- plan_id
- product_id
- variant_id (if applicable)

These are proposed fields. Coordinate the final schema with the team before implementation.

Understand:
- One product can have multiple variants.
- A plan can include multiple products.
- A product can appear in multiple plans.
- The plan-product relationship is many-to-many.

#### Phase 3 — Backend development

Implement endpoints following the agreed API contract.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/products | Create product |
| GET | /api/products | List products |
| GET | /api/products/{id} | View product |
| PUT | /api/products/{id} | Update product |
| DELETE | /api/products/{id} | Delete or archive product |
| POST | /api/products/{id}/variants | Create variant |
| GET | /api/plans | List subscription plans |
| POST | /api/plans | Create subscription plan |
| GET | /api/plans/{id} | View plan |
| PUT | /api/plans/{id} | Update plan |
| DELETE | /api/plans/{id} | Delete or deactivate plan |
| POST | /api/plans/{id}/products | Add products to plan |

Implement:
- Price validation.
- Billing interval validation.
- Product availability checks.
- Duplicate relationship prevention.
- Pagination and filtering.
- Authorization for management operations.

Avoid permanently deleting products or plans already referenced by subscriptions. Prefer deactivation or archival.

#### Phase 4 — Frontend development

Build the following pages:

**Product management**
- Product listing.
- Add product.
- Edit product.
- Product details.
- Product variant management.

**Subscription plan management**
- Plan listing.
- Create plan.
- Edit plan.
- Plan details.
- Add/remove products from plans.

**Customer-facing catalogue**
- Browse available plans.
- View plan details.
- View included products.
- Compare plan prices and billing intervals.

UI requirements:
- Search and filtering.
- Clear price presentation.
- Form validation.
- Confirmation before destructive actions.
- Responsive layouts.

#### Phase 5 — Testing

Test:
- Creating products.
- Editing products.
- Adding variants.
- Creating subscription plans.
- Linking products to plans.
- Invalid prices.
- Invalid billing intervals.
- Duplicate plan-product relationships.
- Inactive products and plans.
- Unauthorized management operations.

### 4. Dependencies

Needs:
- Member 1's authentication and role permissions.
- Agreed database conventions.
- Shared frontend components and API response format.

Provides:
- Product APIs.
- Product variant APIs.
- Subscription plan APIs.
- Plan-product relationships.

Member 3 depends on this module to create quotations and subscriptions using valid products and plans.

### 5. Final deliverables

- Product management module.
- Product variant management.
- Subscription plan management.
- Plan-product relationship management.
- Customer-facing catalogue.
- Backend APIs and frontend pages.
- Automated tests.
- API documentation.

### 6. Definition of completion

The module is complete when authorized staff can manage products and plans, customers can browse available plans, and Member 3 can reliably retrieve the selected plan and its product details.




# MEMBER 3 — QUOTATIONS, SUBSCRIPTIONS AND BILLING
## Brightloop Subscription Management System

### 1. Objective

Build the core business functionality of the application.

This module handles the process of turning a customer's interest in a product or plan into a quotation, an active subscription, invoices, and payment records.

### 2. Responsibilities

- Quotation creation.
- Quotation management.
- Quotation confirmation.
- Subscription creation.
- Subscription lifecycle management.
- Recurring billing.
- Invoice generation.
- Tax calculations.
- Payment recording.
- Invoice and payment history.

### 3. Development roadmap

#### Phase 1 — Understand the foundation

Learn and understand:
- SQLAlchemy relationships.
- Database transactions.
- FastAPI service layers.
- Date and billing calculations.
- Financial calculations and decimal arithmetic.
- Idempotency.
- REST API design.

Review the product and plan schema with Member 2 before implementation.

#### Phase 2 — Database development

Create and manage:

**quotations**
- id
- customer_id
- status
- subtotal
- tax_amount
- total_amount
- valid_until
- created_at

**quotation_items**
- id
- quotation_id
- plan_id
- quantity
- unit_price
- total_price

**subscriptions**
- id
- customer_id
- plan_id
- quotation_id
- status
- start_date
- next_billing_date
- end_date

**invoices**
- id
- subscription_id
- customer_id
- invoice_number
- subtotal
- tax_amount
- total_amount
- due_date
- status

**payments**
- id
- invoice_id
- amount
- payment_method
- payment_reference
- payment_status
- payment_date

Coordinate the final schema with the team. Add appropriate invoice-line-item and tax-detail entities if required.

#### Phase 3 — Quotation development

Implement:
- Create quotation.
- Add products/plans.
- Calculate subtotal.
- Calculate tax.
- Calculate final total.
- Set quotation expiration.
- Confirm or reject quotation.
- Track quotation status.

Quotation workflow:

Draft → Sent → Accepted / Rejected / Expired

#### Phase 4 — Subscription development

Implement:
- Create subscription from an accepted quotation.
- Activate subscription.
- Pause subscription.
- Resume subscription.
- Renew subscription.
- Cancel subscription.
- Track subscription status.
- Calculate next billing date.

Possible lifecycle:

Pending → Active → Paused → Active → Cancelled / Expired

Define allowed transitions and enforce them.

#### Phase 5 — Invoice and billing development

Implement:
- Invoice generation.
- Invoice numbering.
- Billing cycle calculation.
- Tax calculation.
- Invoice due dates.
- Payment recording.
- Payment status updates.
- Invoice history.

Recurring billing must:
- Run according to the agreed schedule.
- Avoid duplicate invoices.
- Handle retries safely.
- Record billing failures.
- Preserve invoice history.

Use decimal-safe monetary calculations rather than floating-point arithmetic.

A payment record is not the same as an actual successful payment gateway transaction. If a gateway is required, coordinate its integration separately.

#### Phase 6 — Backend API development

Suggested endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/quotations | Create quotation |
| GET | /api/quotations | List quotations |
| GET | /api/quotations/{id} | View quotation |
| PATCH | /api/quotations/{id}/status | Update quotation status |
| POST | /api/quotations/{id}/confirm | Confirm quotation |
| POST | /api/subscriptions | Create subscription |
| GET | /api/subscriptions | List subscriptions |
| GET | /api/subscriptions/{id} | View subscription |
| PATCH | /api/subscriptions/{id}/status | Update subscription |
| GET | /api/invoices | List invoices |
| GET | /api/invoices/{id} | View invoice |
| POST | /api/invoices/generate | Generate invoice |
| POST | /api/payments | Record payment |
| GET | /api/payments | View payment history |

These endpoints are proposals and must be reconciled with the team's API contract.

#### Phase 7 — Frontend development

Build:
- Quotation listing.
- Quotation creation form.
- Quotation details.
- Quotation status controls.
- Subscription listing.
- Subscription details.
- Subscription lifecycle controls.
- Invoice listing.
- Invoice details.
- Payment history.
- Payment recording interface.

#### Phase 8 — Testing

Test:
- Quotation totals.
- Tax calculations.
- Quotation acceptance and rejection.
- Subscription creation.
- Invalid lifecycle transitions.
- Billing date calculations.
- Recurring invoice generation.
- Duplicate invoice prevention.
- Partial and full payment recording.
- Overdue invoice status.
- Unauthorized billing actions.

### 4. Dependencies

Needs:
- Member 1: authentication and permissions.
- Member 2: product and plan data.
- Member 4: agreed integration and deployment environment.

Provides:
- Quotation data.
- Subscription data.
- Invoice data.
- Payment data.
- Billing information for dashboards.

### 5. Final deliverables

- Complete quotation workflow.
- Subscription lifecycle management.
- Recurring invoice generation.
- Tax calculations.
- Payment tracking.
- Invoice and payment history.
- Backend APIs.
- Frontend pages.
- Automated tests.

### 6. Definition of completion

A customer must be able to progress through the agreed quotation-to-subscription workflow, generate invoices, and record payments without duplicate billing or incorrect calculations.




# MEMBER 4 — DASHBOARD, ANALYTICS AND INTEGRATION
## Brightloop Subscription Management System

### 1. Objective

Build the dashboards and analytics system while coordinating integration and deployment of the complete application.

This member is also responsible for helping ensure that all four modules work together as one application.

### 2. Responsibilities

- Admin dashboard.
- Staff dashboard.
- Customer dashboard.
- Revenue analytics.
- Subscription analytics.
- Invoice and payment summaries.
- Charts and visualizations.
- Shared application layout.
- Docker setup.
- Integration testing.
- Deployment documentation.

### 3. Development roadmap

#### Phase 1 — Understand the foundation

Learn and understand:
- React component architecture.
- React Router.
- API integration.
- FastAPI response formats.
- PostgreSQL aggregation queries.
- SQLAlchemy queries.
- Docker and Docker Compose.
- Environment variables.
- Integration testing.

Review the existing project architecture before creating a new structure.

#### Phase 2 — Shared frontend foundation

Coordinate the common frontend structure.

Create or coordinate:
- Shared navigation.
- Sidebar.
- Header.
- Dashboard layout.
- Reusable cards.
- Reusable tables.
- Loading and error states.
- Responsive layout conventions.

Do not duplicate components that other members are already building.

#### Phase 3 — Dashboard development

**Admin dashboard**
- Total users.
- Total customers.
- Active subscriptions.
- Paused subscriptions.
- Cancelled subscriptions.
- Total invoices.
- Outstanding invoices.
- Revenue summary.
- Recent activity.

**Staff dashboard**
- Assigned work or relevant operational summaries.
- Recent quotations.
- Active subscriptions.
- Pending invoices.
- Relevant customer information.

**Customer dashboard**
- Current subscription.
- Subscription status.
- Next billing date.
- Recent invoices.
- Payment history.
- Available plans.

Only display features supported by actual backend data.

#### Phase 4 — Analytics development

Build charts and reports for:
- Monthly revenue.
- Subscription growth.
- Active versus cancelled subscriptions.
- Plan popularity.
- Invoice payment status.
- Outstanding balances.

Implement:
- Date-range filtering.
- Accurate aggregation.
- Empty-state handling.
- Clear labels and currency formatting.

Dashboard values must come from the database through APIs, not hardcoded values.

#### Phase 5 — Backend development

Coordinate and implement dashboard endpoints.

Suggested endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/dashboard/admin | Admin summary |
| GET | /api/dashboard/staff | Staff summary |
| GET | /api/dashboard/customer | Customer summary |
| GET | /api/analytics/revenue | Revenue analytics |
| GET | /api/analytics/subscriptions | Subscription analytics |
| GET | /api/analytics/invoices | Invoice analytics |

Coordinate authorization with Member 1 and data availability with Members 2 and 3.

#### Phase 6 — Docker and deployment

Create:
- Frontend Dockerfile.
- Backend Dockerfile.
- PostgreSQL service configuration.
- Docker Compose configuration.
- Environment variable examples.
- Database initialization and migration instructions.

Ensure:
- Secrets are not hardcoded.
- Database credentials are configurable.
- Migrations can run on a fresh database.
- Persistent database storage is configured.
- The frontend can communicate with the backend.
- The application starts reliably.

#### Phase 7 — Integration testing

Coordinate the complete application workflow:

1. Register and log in.
2. Create or manage products.
3. Create subscription plans.
4. Create quotations.
5. Confirm quotations.
6. Create subscriptions.
7. Generate invoices.
8. Record payments.
9. Verify dashboard statistics.

Test each role's access and make sure dashboard figures match actual database records.

#### Phase 8 — Final deployment

- Run the complete application through Docker Compose.
- Test from a clean setup.
- Verify migrations.
- Verify frontend-backend connectivity.
- Load demo data.
- Fix deployment issues.
- Prepare deployment documentation.
- Coordinate the final demo.

### 4. Dependencies

Needs:
- Member 1: user and role information.
- Member 2: products and plans.
- Member 3: subscriptions, invoices, payments and revenue data.

Provides:
- Dashboard APIs.
- Analytics.
- Shared UI conventions.
- Docker configuration.
- Integration and deployment support.

### 5. Final deliverables

- Admin dashboard.
- Staff dashboard.
- Customer dashboard.
- Analytics and charts.
- Dashboard APIs.
- Shared UI components.
- Docker configuration.
- Integration tests.
- Deployment documentation.

### 6. Definition of completion

The dashboards must display accurate information from the integrated database, each role must see only authorized information, and the entire application must start successfully using the agreed deployment process.