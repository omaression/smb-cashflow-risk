# Deployment Notes

## Production deployment architecture

```
cashflow.omaression.com       -> Vercel (Next.js frontend)
cashflow-api.omaression.com   -> Cloudflare Tunnel -> VPS FastAPI API
VPS PostgreSQL                -> Docker volume at /mnt/volume-1/data/smb-cashflow-risk/postgres
Cloudflare                    -> DNS + API tunnel routing
```

- **Frontend** deployed to Vercel from `apps/web/`
- **API** served at `https://cashflow-api.omaression.com/api/v1`
- **API docs** served at `https://cashflow-api.omaression.com/docs`
- **Database** is VPS-hosted PostgreSQL in a private Docker network and persisted at `/mnt/volume-1/data/smb-cashflow-risk/postgres`
- **API to database host** is `smb-cashflow-risk-postgres`
- **Render-specific instructions** live in `docs/deploy-render.md` and are legacy or backup-specific
- **CORS** configured via `ALLOWED_ORIGINS` environment variable on the API

See `docs/deploy-vps-cloudflare.md` for current production deployment instructions. See `docs/deploy-render.md` only for the legacy Render-specific path.

## Canonical API hostname
`https://cashflow-api.omaression.com` is the canonical production API hostname.

The previous hostname, `https://api.cashflow.omaression.com`, is deprecated and should not be used in app environment variables. It was replaced to avoid the multi-level subdomain pattern under Cloudflare Universal SSL. The current first-level subdomain, `cashflow-api.omaression.com`, is the supported production API hostname.

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
./scripts/seed-remote.sh https://cashflow-api.omaression.com
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
- production value for both is `https://cashflow-api.omaression.com/api/v1`
- uses Next.js standalone output in the runner image
- serves production build on port 3000

## Local requirements
- Docker Engine 24+ and Docker Compose v2
- No local Python or Node.js installation needed
- `curl` is required on the host to run `scripts/seed-docker.sh`
- The `str | None` union syntax in Python source requires Python 3.10+; the container uses 3.12 so this is handled automatically

## Production considerations
The local Docker stack is good for demos and portfolio evaluation. Current production runs the API and PostgreSQL on a VPS behind Cloudflare Tunnel. Before scaling beyond portfolio use, consider:
- migration workflow (Alembic or equivalent)
- persistent secrets handling
- health/readiness endpoints for container orchestration
- backup restore drills
- non-default credentials and private database networking

## Smoke checks
After startup:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/api/v1/dashboard/summary
open http://localhost:3000
```
