# Target Project Structure

```text
brightloop/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/                 # Router, providers, app bootstrap
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   └── forms/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── products/
│   │   │   ├── plans/
│   │   │   ├── quotations/
│   │   │   ├── subscriptions/
│   │   │   ├── billing/
│   │   │   └── dashboard/
│   │   ├── layouts/
│   │   ├── lib/                 # API client, shared helpers
│   │   ├── hooks/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   ├── core/                # Config, security, logging
│   │   ├── db/                  # Engine, session, base
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── workers/             # Scheduled job entrypoints
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── Dockerfile
│
├── docs/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── CONTRIBUTING.md
```

## Module ownership
- Member 1: `auth` feature, user model/auth endpoints and auth UI. Coordinate shared core/db files with the team.
- Member 2: `products` and `plans` feature modules, product/variant/plan models, schemas, services, endpoints and UI.
- Member 3: `quotations`, `subscriptions`, `billing`, `payments` modules and billing worker.
- Member 4: dashboard/analytics UI and API integration, shared layout, Docker/deployment coordination.

## Shared files
Only one person should make a change to shared files at a time, agreed in team chat:
- `backend/app/main.py`
- `backend/app/db/*`
- `backend/app/core/config.py`
- `backend/app/api/v1/router.py`
- `frontend/src/app/*`
- `frontend/src/lib/api.js`
- `docker-compose.yml`
- root `.env.example`

The owner of a shared file should announce changes and keep the team informed.
