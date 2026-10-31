# Brightloop — Subscription Management System

A team-built subscription platform for managing products, plans, quotations, subscriptions, recurring invoices, payments and revenue reporting.

## Technology
- Frontend: React + Vite
- Backend: FastAPI
- Database: PostgreSQL
- ORM and migrations: SQLAlchemy 2.x + Alembic
- Validation: Pydantic
- Containers: Docker + Docker Compose
- API style: REST / JSON

## Team
| Member | Ownership | Branch |
|---|---|---|
| Member 1 | Authentication and user/role management | `auth` |
| Member 2 | Products, variants and plans | `products` |
| Member 3 | Subscriptions, billing, invoices and payments | `billing` |
| Member 4 | Dashboards, analytics, frontend integration and deployment coordination | `dashboard` |

The repository is shared. Each member works on their own branch and merges through reviewed pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

## Repository layout
```text
brightloop/
├── frontend/                 # React application
├── backend/                  # FastAPI application
├── docs/                     # Team and technical documentation
├── .github/                  # PR and issue templates
├── CHANGELOG.md              # Completed changes log
├── TEAM_STATUS.md            # Active tasks and progress
├── AI_CONTEXT.md             # Shared AI instructions and architecture
├── docker-compose.yml
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```

The detailed target structure is in [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

## Quick start
1. Install Git, Docker Desktop and Docker Compose.
2. Clone the repository.
3. Copy `.env.example` to `.env` and set local values.
4. Run `docker compose up --build`.
5. Apply database migrations from the backend container.
6. Open the frontend and API documentation URLs listed in [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

Do not commit `.env`, passwords, tokens, database dumps or real customer data.

## Project status
This repository documentation defines the agreed starting architecture and team contracts. A feature is not complete until its tests pass, its API/UI integration works, and its documentation is updated.

## Development tracking and AI context
- [Changelog](CHANGELOG.md) — Completed work log
- [Team status](TEAM_STATUS.md) — Active tasks and who is working on what
- [AI context and instructions](AI_CONTEXT.md) — Shared architecture guide and mandatory rules for AI agents
- [Master AI instructions](docs/BRIGHTLOOP_MASTER_AI_INSTRUCTIONS.md) — Comprehensive technical guidelines

## Documentation index
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Project structure](docs/PROJECT_STRUCTURE.md)
- [Database design](docs/DATABASE_SCHEMA.md)
- [API conventions and contracts](docs/API_CONTRACTS.md)
- [Team responsibilities](docs/TEAM_RESPONSIBILITIES.md)
- [Git workflow](docs/GIT_WORKFLOW.md)
- [Local setup](docs/LOCAL_SETUP.md)
- [Environment variables](docs/ENVIRONMENT.md)
- [Testing strategy](docs/TESTING.md)
- [Security checklist](docs/SECURITY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Definition of done](docs/DEFINITION_OF_DONE.md)
- [Meeting notes](docs/MEETING_NOTES.md)
- [Decision records](docs/adr/README.md)
