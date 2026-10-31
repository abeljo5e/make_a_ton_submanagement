# Product Requirements — Brightloop

## 1. Purpose
Brightloop is a subscription-management platform for a fictional SaaS provider. It centralizes customer accounts, products, pricing plans, quotations, subscriptions, recurring invoices, payments and revenue reporting.

## 2. User roles
### Admin
- Manage products, variants, plans, tax and discount configuration.
- Create and manage staff accounts.
- View and manage customers, subscriptions, invoices and payments.
- Access analytics, audit logs and system settings.

### Staff
- Manage customer records within granted permissions.
- Create quotations and convert accepted quotations into subscriptions.
- View and manage subscriptions, invoices and payment records.
- Cannot create staff/admin accounts or change restricted system settings.

### Customer
- Register and sign in.
- View only their own profile, subscriptions, invoices and payments.
- View upcoming renewal/billing dates.
- Request pause or cancellation where the plan allows it.
- Download their invoices.

## 3. Functional requirements
### Authentication
- Email must be unique.
- Password must be longer than eight characters and include uppercase, lowercase and special characters.
- Passwords must be securely hashed.
- Password reset must use expiring, single-use tokens delivered to the registered email.
- All protected endpoints must enforce role and resource ownership on the server.

### Products and variants
- Admin can create, view, update and deactivate products.
- Product fields: name, type, sales price, cost price, notes and status.
- A product may have multiple variants.
- A variant has a name and additional price.
- Price calculations must use decimal arithmetic, not binary floating point.

### Plans
- Admin can create, view, update and deactivate plans.
- A plan has a name, description, price, billing frequency, minimum quantity, availability dates and policy flags.
- Billing frequencies: daily, weekly, monthly and yearly.
- Policy flags: automatic closure, early cancellation, pause and renewal.
- Plans may include multiple products with quantities.

### Quotations
- Staff can create quotations from reusable templates.
- Quotations contain customer, validity/expiry, product lines, quantities, taxes, discounts and totals.
- Accepted, unexpired quotations can be converted into subscriptions.
- Conversion must not create duplicate subscriptions.

### Subscriptions
- Each subscription has a unique number, customer, plan, start/expiry dates, next billing date, payment terms, lines, totals and status.
- Main lifecycle: Draft → Quotation → Confirmed → Active → Closed.
- Allowed additional transitions include Active ↔ Paused and Active → Closed/Renewed, subject to business rules.
- Every transition must be validated and recorded.

### Invoices and billing
- Invoices are generated from eligible subscriptions.
- Invoice lines preserve product description, quantity, unit price, tax and discount snapshots.
- Billing supports daily, weekly, monthly and yearly cycles.
- Billing must be idempotent: retries or concurrent workers must not create duplicate invoices for the same subscription and billing period.
- Invoice states: Draft, Confirmed, Paid, Cancelled.
- Cancelled and paused subscriptions must not be billed.
- A scheduled job and an admin-triggered run should use the same billing service.

### Payments
- Record payment reference, invoice, amount, method, date, status and provider transaction ID when applicable.
- Support partial and full payments.
- An invoice is Paid only when successful payments cover its amount due.
- A simulated payment must be clearly labelled as a demo and must never be represented as a real transaction.

### Analytics
- Display active subscriptions, MRR, ARR, collected revenue, invoiced revenue, outstanding invoices, renewals and churn.
- Dashboard metrics must be calculated from database records, not hardcoded values.
- Metric definitions must be documented and consistent.

## 4. Non-functional requirements
- Responsive, accessible interface.
- Server-side authorization and validation.
- PostgreSQL as the deployment database.
- Database migrations through Alembic.
- Docker-based reproducible development.
- Environment-based configuration and secret management.
- Automated tests for critical business rules.
- Structured logs and useful error responses.
- Public deployment must use persistent database storage and HTTPS.

## 5. Acceptance criteria
A release candidate must demonstrate:
1. A customer can register and sign in.
2. Admin can create a product, variant and plan.
3. Staff can create a quotation and convert it to a subscription.
4. An eligible subscription generates one invoice for a billing period.
5. Retrying the billing job does not duplicate that invoice.
6. A payment updates the invoice balance and status correctly.
7. A customer cannot access another customer's records.
8. Dashboard figures are derived from stored data.
