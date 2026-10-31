# Security Checklist

## Authentication
- Hash passwords using Argon2id or bcrypt through a maintained library.
- Never store plaintext passwords or reset tokens.
- Reset tokens must be random, single-use, expiring and stored hashed.
- Rate-limit login and password reset endpoints where practical.

## Authorization
- Enforce roles on the backend.
- Check record ownership on every customer-scoped request.
- Do not trust user IDs or roles supplied by the browser.
- Default to deny when permission is unclear.

## Data and API
- Validate all input with Pydantic.
- Use SQLAlchemy parameterized queries; never build SQL from untrusted strings.
- Restrict CORS to known origins.
- Avoid leaking stack traces or sensitive data in production errors.
- Use HTTPS in production.
- Apply request size limits where appropriate.

## Secrets and deployment
- Never commit `.env`, API keys, tokens or private certificates.
- Use host secret management.
- Keep dependencies updated.
- Use non-root containers where practical.
- Keep PostgreSQL private; do not expose it publicly without a strong reason.
- Back up the persistent database and test restoration.

## Billing integrity
- Use database transactions.
- Enforce invoice uniqueness per subscription billing period.
- Verify payment provider signatures if integrating a real provider.
- Never mark a payment successful based only on a browser redirect.
- Keep audit trails for sensitive actions.
