# API Contracts and Team Integration Agreement

Base URL: `/api/v1`

All request and response bodies use JSON unless an endpoint explicitly returns a file.

## General conventions
- Use plural resource names.
- Use lowercase, hyphen-separated URL paths.
- Return appropriate HTTP status codes.
- Use ISO 8601 timestamps in UTC.
- Represent monetary values as decimal strings in JSON, e.g. `"1250.00"`, to avoid precision loss.
- Use UUIDs for public resource IDs unless the team explicitly chooses integer IDs before implementation.
- Paginate collection endpoints.
- Never expose password hashes, reset tokens or internal secrets.

## Standard error shape
```json
{
  "detail": "Human-readable explanation",
  "code": "VALIDATION_ERROR"
}
```
FastAPI's default validation response may be retained initially, but the team should agree on one consistent error shape before frontend integration.

## Authentication — Member 1
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Customer registration |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout if using server-managed sessions |
| POST | `/auth/forgot-password` | Request reset |
| POST | `/auth/reset-password` | Consume reset token |
| GET | `/auth/me` | Current user |
| POST | `/staff` | Admin creates staff |

## Products and plans — Member 2
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/products` | List/search products |
| POST | `/products` | Create product |
| GET | `/products/{product_id}` | Product details and variants |
| PATCH | `/products/{product_id}` | Update product |
| POST | `/products/{product_id}/deactivate` | Deactivate product |
| POST | `/products/{product_id}/variants` | Add variant |
| PATCH | `/variants/{variant_id}` | Update variant |
| DELETE | `/variants/{variant_id}` | Remove variant if unused |
| GET | `/plans` | List plans |
| POST | `/plans` | Create plan |
| GET | `/plans/{plan_id}` | Plan details and products |
| PATCH | `/plans/{plan_id}` | Update plan |
| POST | `/plans/{plan_id}/deactivate` | Deactivate plan |

## Quotations and subscriptions — Member 3
| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/quotations` | List/create quotations |
| GET/PATCH | `/quotations/{id}` | View/update quotation |
| POST | `/quotations/{id}/confirm` | Confirm quotation |
| POST | `/quotations/{id}/convert` | Convert to subscription |
| GET/POST | `/subscriptions` | List/create subscriptions |
| GET | `/subscriptions/{id}` | Subscription details |
| POST | `/subscriptions/{id}/pause` | Pause |
| POST | `/subscriptions/{id}/resume` | Resume |
| POST | `/subscriptions/{id}/cancel` | Cancel/close |
| POST | `/subscriptions/{id}/renew` | Renew |

## Invoices and payments — Member 3
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/invoices` | List invoices |
| GET | `/invoices/{id}` | Invoice details |
| POST | `/invoices/{id}/confirm` | Confirm invoice |
| POST | `/invoices/{id}/cancel` | Cancel invoice |
| GET | `/invoices/{id}/pdf` | Download invoice PDF |
| GET/POST | `/payments` | List/record payments |
| POST | `/billing/run` | Admin-triggered billing run |

## Dashboard — Member 4
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/dashboard/summary` | KPI summary |
| GET | `/dashboard/revenue` | Revenue time series |
| GET | `/dashboard/subscriptions` | Subscription metrics |
| GET | `/dashboard/invoices` | Invoice metrics |

## Example product response
```json
{
  "id": "uuid",
  "name": "Business ERP",
  "type": "software",
  "sales_price": "2000.00",
  "cost_price": "800.00",
  "currency": "INR",
  "status": "active",
  "variants": [
    {
      "id": "uuid",
      "name": "Odoo",
      "additional_price": "560.00"
    }
  ]
}
```

## Example plan response
```json
{
  "id": "uuid",
  "name": "Professional Monthly",
  "price": "2500.00",
  "billing_frequency": "monthly",
  "minimum_quantity": 1,
  "available_from": "2026-11-01",
  "available_until": "2026-12-31",
  "auto_close": true,
  "allow_early_cancellation": true,
  "allow_pause": true,
  "allow_renewal": true,
  "products": [
    {"product_id": "uuid", "quantity": 1}
  ]
}
```

These are proposed contracts. Team members must agree on them before implementation. If a contract changes, update this file and notify every consumer.
