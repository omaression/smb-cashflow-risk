# Deployment Notes

## Local containerized stack
This project can now run as a 3-service Docker stack:
- PostgreSQL
- FastAPI backend
- Next.js frontend

### Start the stack
```bash
docker compose up --build
```

### Endpoints
- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- API base: `http://localhost:8000/api/v1`

## Services
### Database
- image: `postgres:16-alpine`
- default DB: `smb_cashflow_risk`
- default user/password: `postgres` / `postgres`

### API
- built from `apps/api/Dockerfile`
- expects `DATABASE_URL`
- runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Web
- built from `apps/web/Dockerfile`
- uses `NEXT_PUBLIC_API_BASE_URL`
- serves production build on port 3000

## Production considerations
This stack is good for local demos and portfolio evaluation. Before real deployment, add:
- migration workflow (Alembic or equivalent)
- persistent secrets handling
- CORS policy for deployed frontend/backend split
- health/readiness endpoints for container orchestration
- reverse proxy / TLS termination
- non-default credentials and managed Postgres

## Recommended deploy targets
For a portfolio deploy, the easiest path is:
1. managed Postgres
2. backend container on Render/Fly.io/Railway
3. frontend on Vercel or container host

## Smoke checks
After startup:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/api/v1/dashboard/summary
open http://localhost:3000
```
