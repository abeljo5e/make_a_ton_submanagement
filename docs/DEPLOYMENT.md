# Deployment Guide

## Target deployment
- React frontend: static hosting or frontend container hosting.
- FastAPI backend: container-based application hosting.
- PostgreSQL: managed PostgreSQL or persistent database service.
- Optional worker: separate process/container using the same backend image and database.

## Before deployment
- Set `APP_ENV=production`.
- Configure strong secrets in the hosting dashboard.
- Set `DATABASE_URL` to the provider's PostgreSQL connection string.
- Set exact production CORS origins.
- Set frontend `VITE_API_BASE_URL` to the public backend URL.
- Run Alembic migrations.
- Create an initial admin through a secure one-time process; do not ship a public default admin password.
- Configure SMTP only if email flows are enabled.
- Configure health checks and logs.

## Docker
Build and run locally first:
```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f
```

## Production requirements
- Use a production ASGI server such as Uvicorn workers managed by Gunicorn or the platform's supported process command.
- Do not use FastAPI's development reload mode.
- Use persistent PostgreSQL storage.
- Ensure scheduled billing runs in only the intended worker/scheduler configuration.
- Use a lock/idempotency constraint so multiple app instances cannot double-bill.
- Configure backups and test restoration.
- Use HTTPS.
- Do not expose database ports publicly unless required and secured.

## Release checklist
- [ ] Frontend deployed.
- [ ] Backend deployed and health endpoint responds.
- [ ] Database provisioned and persistent.
- [ ] Migrations applied.
- [ ] CORS and API URL correct.
- [ ] Secrets configured outside Git.
- [ ] Demo data seeded safely.
- [ ] Critical user journey tested on public URLs.
- [ ] Logs and backups checked.
