# Render Deployment Guide

> Legacy / Render-specific guide. Current production uses VPS-hosted FastAPI at `https://cashflow-api.omaression.com/api/v1` and VPS-hosted PostgreSQL. Use `docs/deploy-vps-cloudflare.md` for the current production API and database deployment.

## Overview
This guide covers the Render-specific deployment path:
- **Vercel** - Next.js frontend
- **Render** - FastAPI API and managed PostgreSQL

Render can also host a backup frontend web service for redundancy. This is an alternative deployment path, not the current production API/database architecture.

## Files
- `render.yaml` - Render blueprint for API, backup web, and database
- `apps/web/vercel.json` - Vercel project config for the Next.js frontend

## Render deployment steps
1. Push `main` to GitHub.
2. In Render, create a new Blueprint deployment from the repo.
3. Confirm the following resources:
   - `smb-cashflow-risk-db` (PostgreSQL)
   - `smb-cashflow-risk-api` (FastAPI)
   - `smb-cashflow-risk-web` (backup frontend)
4. Wait for the database to provision and services to build.
5. If you are using the legacy Render hostname, verify the API at its Render-mapped docs URL.

## Vercel deployment steps
1. Import the repo in Vercel.
2. Set the root directory to `apps/web`.
3. Set environment variables for the API you intend to use:
   - Current production API: `https://cashflow-api.omaression.com/api/v1`
   - Alternative Render API: `https://<render-api-host>/api/v1`
4. Deploy. Vercel auto-detects Next.js.

## Cloudflare DNS
Add two CNAME records (proxied):
- `cashflow` -> Vercel deployment URL (e.g., `cname.vercel-dns.com`)
- `api.cashflow` -> Render API service URL (legacy example: `smb-cashflow-risk-api.onrender.com`)

The legacy `api.cashflow.omaression.com` hostname is not the current production API. Current production uses `cashflow-api.omaression.com`.

## Seeding demo data on hosted deploy
```bash
./scripts/seed-remote.sh https://<render-api-host>
```

## Required follow-up checks
- API docs reachable at `/docs`
- Web dashboard loads successfully
- CORS headers present (check browser console)
- API/web environment variables point to the deployed API URL, not localhost

## Environment variables

### API (Render)
| Variable | Value |
|----------|-------|
| `APP_ENV` | `production` |
| `DATABASE_URL` | from Render managed Postgres |
| `ALLOWED_ORIGINS` | `https://cashflow.omaression.com` |

### Web (Vercel)
| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://<render-api-host>/api/v1` |
| `INTERNAL_API_BASE_URL` | `https://<render-api-host>/api/v1` |
