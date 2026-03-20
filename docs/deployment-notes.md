# Deployment Notes

## Production deployment architecture

```
cashflow.omaression.com       → Vercel (Next.js frontend)
api.cashflow.omaression.com   → Render (FastAPI API)
Render managed PostgreSQL      → internal connection
Cloudflare                     → DNS + proxy
```

- **Frontend** deployed to Vercel from `apps/web/`
- **API** deployed to Render via Docker from `apps/api/Dockerfile`
- **Database** provisioned as Render managed PostgreSQL (starter plan)
- **Render web service** kept as a backup frontend deployment option
- **CORS** configured via `ALLOWED_ORIGINS` environment variable on the API

See `docs/deploy-render.md` for step-by-step deployment instructions.

## Local containerized stack
This project can also run as a 3-service Docker stack:
- PostgreSQL
- FastAPI backend
- Next.js frontend

### Start the stack
```bash
docker compose up --build -d
```

### Seed the database
On first run, the schema is auto-applied by Postgres. Seed sample data via:
```bash
./scripts/seed-docker.sh
```

This imports sample CSV files from `data/raw/` through the API import endpoint.

### Seed a hosted deployment
```bash
./scripts/seed-remote.sh https://api.cashflow.omaression.com
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
- expects `DATABASE_URL` and `ALLOWED_ORIGINS`
- runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Web
- built from `apps/web/Dockerfile`
- uses `NEXT_PUBLIC_API_BASE_URL` for browser-visible links
- uses `INTERNAL_API_BASE_URL` for server-side API calls
- uses Next.js standalone output in the runner image
- serves production build on port 3000

## Requirements
- Docker Engine 24+ and Docker Compose v2
- No local Python or Node.js installation needed
- `curl` is required on the host to run `scripts/seed-docker.sh`
- The `str | None` union syntax in Python source requires Python 3.10+; the container uses 3.12 so this is handled automatically

## Production considerations
This stack is good for local demos and portfolio evaluation. Before scaling beyond portfolio use, consider:
- migration workflow (Alembic or equivalent)
- persistent secrets handling
- health/readiness endpoints for container orchestration
- reverse proxy / TLS termination
- non-default credentials and managed Postgres

## Smoke checks
After startup:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/api/v1/dashboard/summary
open http://localhost:3000
```
