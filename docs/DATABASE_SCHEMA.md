# Database Schema — Initial Proposal

Use PostgreSQL and SQLAlchemy 2.x. Use Alembic migrations for every schema change. Do not manually edit production tables.

## Proposed entities
| Table | Main purpose | Owner |
|---|---|---|
| users | Login identity, email, password hash, role, status | Member 1 |
| password_reset_tokens | Hashed, expiring reset tokens | Member 1 |
| customers | Customer business/profile details linked to user | Member 1 / agree ownership |
| products | Product catalog and base prices | Member 2 |
| product_variants | Variant and additional price | Member 2 |
| plans | Billing frequency, price, availability and policy | Member 2 |
| plan_products | Plan-to-product association and quantity | Member 2 |
| quotation_templates | Reusable quotation templates | Member 3 |
| quotations | Quotation header/status/expiry | Member 3 |
| quotation_lines | Quoted products, variants and price snapshots | Member 3 |
| subscriptions | Customer, plan, lifecycle and billing dates | Member 3 |
| subscription_lines | Product, variant, quantity and price snapshots | Member 3 |
| invoices | Invoice header, totals, dates and status | Member 3 |
| invoice_lines | Immutable invoice line snapshots | Member 3 |
| payments | Payment attempts/records and references | Member 3 |
| billing_runs | Scheduled/manual run tracking | Member 3 |
| audit_logs | Important actions and actor metadata | Shared / agree owner |

## Relationship overview
```text
users 1---0..1 customers
products 1---many product_variants
plans many---many products (through plan_products)
customers 1---many quotations
quotations 1---many quotation_lines
customers 1---many subscriptions
plans 1---many subscriptions
subscriptions 1---many subscription_lines
subscriptions 1---many invoices
invoices 1---many invoice_lines
invoices 1---many payments
users 1---many audit_logs
```

## Data rules
- Prefer UUID primary keys for public-facing records.
- Use `NUMERIC(12,2)` or suitable precision for money; map to Python `Decimal`.
- Store currency explicitly (e.g. `INR`).
- Use timezone-aware timestamps and store UTC.
- Add created/updated timestamps to mutable records.
- Add foreign keys and indexes for frequently filtered columns.
- Use database uniqueness constraints for email, invoice number and billing idempotency.
- Invoice and quotation lines must snapshot names, quantities, prices, taxes and discounts so later catalog changes do not rewrite history.
- Deactivation is generally safer than hard deletion for records referenced by transactions.

## Billing idempotency
A subscription should not receive two invoices for the same billing period. Add a unique constraint such as `(subscription_id, billing_period_start, billing_period_end)` on the invoice/billing-period record. Enforce it in PostgreSQL, not only in Python.

## Before creating migrations
Members must agree on ID type, naming convention, deletion policy, currency handling and ownership of shared models. Do not let two branches independently create conflicting definitions of the same table.
