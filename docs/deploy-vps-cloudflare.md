# VPS and Cloudflare Deployment

## Purpose
This is the current production API and database deployment guide for `smb-cashflow-risk`.

- Frontend: Vercel at `https://cashflow.omaression.com`
- API: VPS-hosted FastAPI behind Cloudflare Tunnel at `https://cashflow-api.omaression.com`
- API base path: `https://cashflow-api.omaression.com/api/v1`
- API docs: `https://cashflow-api.omaression.com/docs`
- Database: private VPS-hosted PostgreSQL container

## Architecture
```text
cashflow.omaression.com       -> Vercel (Next.js frontend)
cashflow-api.omaression.com   -> Cloudflare Tunnel -> 127.0.0.1:8000 on VPS
smb-cashflow-risk-api         -> FastAPI container
smb-cashflow-risk-postgres    -> PostgreSQL container on smb_cashflow_net
PostgreSQL data               -> /mnt/volume-1/data/smb-cashflow-risk/postgres
Backups                       -> /mnt/volume-1/data/smb-cashflow-risk/backups
```

## Services
- `smb-cashflow-risk-api`: FastAPI application container.
- `smb-cashflow-risk-postgres`: private PostgreSQL container.
- `cloudflared`: Cloudflare Tunnel process that publishes the API hostname.

## Persistent paths
- PostgreSQL data: `/mnt/volume-1/data/smb-cashflow-risk/postgres`
- Database backups: `/mnt/volume-1/data/smb-cashflow-risk/backups`

## Docker network
Use the private Docker network:

```text
smb_cashflow_net
```

The API connects to PostgreSQL over this network using host `smb-cashflow-risk-postgres`.

## API environment
```bash
APP_ENV=production
ALLOWED_ORIGINS=https://cashflow.omaression.com
DATABASE_URL=postgresql+psycopg://smb_cashflow_risk:<password>@smb-cashflow-risk-postgres:5432/smb_cashflow_risk
```

Do not commit real database passwords, tunnel tokens, or private host values.

## Vercel frontend environment
```bash
NEXT_PUBLIC_API_BASE_URL=https://cashflow-api.omaression.com/api/v1
INTERNAL_API_BASE_URL=https://cashflow-api.omaression.com/api/v1
API_BASE_URL=https://cashflow-api.omaression.com/api/v1
```

`API_BASE_URL` is optional and can be used for server-side fallback configuration.

## Cloudflare DNS
Create a proxied `cashflow-api` CNAME that points to the Cloudflare Tunnel target or tunnel-managed hostname.

```text
cashflow-api.omaression.com -> Cloudflare Tunnel target
Proxy status: proxied
```

## Cloudflare Tunnel public hostname
Configure the tunnel public hostname:

```text
Hostname: cashflow-api.omaression.com
Service: http://127.0.0.1:8000
```

## Validation
Run these from the VPS or an operator workstation as appropriate:

```bash
curl -i http://127.0.0.1:8000/healthz
curl -i https://cashflow-api.omaression.com/healthz
curl -sS https://cashflow-api.omaression.com/api/v1/dashboard/summary | jq .
```

## Seeding
Seed locally on the VPS first, then verify the public API.

```bash
./scripts/seed-remote.sh http://127.0.0.1:8000
curl -sS http://127.0.0.1:8000/api/v1/dashboard/summary | jq .
curl -sS https://cashflow-api.omaression.com/api/v1/dashboard/summary | jq .
```

## Backups
Use `pg_dump` custom format for PostgreSQL backups and store generated backup files under:

```text
/mnt/volume-1/data/smb-cashflow-risk/backups
```

Keep restore steps tested before relying on a backup process for operational recovery.

## Security notes
- PostgreSQL is private and not publicly exposed.
- The API is exposed through Cloudflare Tunnel.
- Do not expose port `5432` publicly.
- Do not commit database credentials, tunnel tokens, or private values.
