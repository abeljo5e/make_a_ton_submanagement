# Environment Variables

Keep real values in local `.env` files or the hosting provider's secret manager. Commit only `.env.example` with safe placeholders.

## Root / Compose
| Variable | Purpose | Example |
|---|---|---|
| `POSTGRES_DB` | Database name | `brightloop` |
| `POSTGRES_USER` | Local DB user | `brightloop_user` |
| `POSTGRES_PASSWORD` | Local DB password | placeholder |
| `DATABASE_URL` | Backend DB connection | `postgresql+psycopg://...` |

## Backend
| Variable | Purpose |
|---|---|
| `APP_ENV` | development/test/production |
| `SECRET_KEY` | Application secret |
| `DATABASE_URL` | SQLAlchemy connection string |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime if JWT is used |
| `SMTP_HOST` | Email server |
| `SMTP_PORT` | Email server port |
| `SMTP_USERNAME` | Email account |
| `SMTP_PASSWORD` | Email credential |
| `FRONTEND_URL` | Public frontend origin |

## Frontend
| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Public backend API base URL |

Vite variables prefixed with `VITE_` are exposed to browser code. Never put secrets in them.

## Security
- Generate strong, unique secrets for each environment.
- Do not reuse development credentials in production.
- Rotate any secret accidentally committed.
- Do not print secrets in logs.
