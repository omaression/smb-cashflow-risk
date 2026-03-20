# Render Deployment Guide

## Overview
The production deployment splits across two platforms:
- **Vercel** — Next.js frontend (primary)
- **Render** — FastAPI API + managed PostgreSQL

Render also hosts a backup frontend web service for redundancy.

## Files
- `render.yaml` — Render blueprint for API, backup web, and database
- `apps/web/vercel.json` — Vercel project config for the Next.js frontend

## Render deployment steps
1. Push `main` to GitHub.
2. In Render, create a new Blueprint deployment from the repo.
3. Confirm the following resources:
   - `smb-cashflow-risk-db` (PostgreSQL)
   - `smb-cashflow-risk-api` (FastAPI)
   - `smb-cashflow-risk-web` (backup frontend)
4. Wait for the database to provision and services to build.
5. After deploy, verify the API at `https://api.cashflow.omaression.com/docs`.

## Vercel deployment steps
1. Import the repo in Vercel.
2. Set the root directory to `apps/web`.
3. Set environment variables:
   - `NEXT_PUBLIC_API_BASE_URL=https://api.cashflow.omaression.com/api/v1`
   - `INTERNAL_API_BASE_URL=https://api.cashflow.omaression.com/api/v1`
4. Deploy. Vercel auto-detects Next.js.

## Cloudflare DNS
Add two CNAME records (proxied):
- `cashflow` → Vercel deployment URL (e.g., `cname.vercel-dns.com`)
- `api.cashflow` → Render API service URL (e.g., `smb-cashflow-risk-api.onrender.com`)

## Seeding demo data on hosted deploy
```bash
./scripts/seed-remote.sh https://api.cashflow.omaression.com
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
| `NEXT_PUBLIC_API_BASE_URL` | `https://api.cashflow.omaression.com/api/v1` |
| `INTERNAL_API_BASE_URL` | `https://api.cashflow.omaression.com/api/v1` |
