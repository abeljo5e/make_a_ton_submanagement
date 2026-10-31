# Local Development Setup

## Prerequisites
- Git
- Docker Desktop with Docker Compose
- A code editor
- Optional for running outside Docker: supported Python and Node.js versions agreed by the team

## First-time setup
```bash
git clone https://github.com/TEAM-OWNER/Subscription-Management-System.git
cd Subscription-Management-System
cp .env.example .env
```
Edit `.env` with local-only values. Never commit it.

## Start services
```bash
docker compose up --build
```

## Common commands
```bash
docker compose ps
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
docker compose down -v
```
Warning: `docker compose down -v` removes named volumes and can delete local database data. Do not use it casually.

## Database migrations
The exact command depends on the final backend image/service name. Typical command:
```bash
docker compose exec backend alembic upgrade head
```

## API documentation
FastAPI normally exposes:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

## Troubleshooting
- Port already in use: change the host port mapping in Compose.
- Database connection refused: check that PostgreSQL is healthy and the backend uses the Compose service hostname, not `localhost`.
- Missing environment variable: compare `.env` with `.env.example`.
- Frontend API errors: verify the frontend API base URL and backend CORS origins.
- Migration errors: inspect migration history and coordinate before editing shared migrations.
