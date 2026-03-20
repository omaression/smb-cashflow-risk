# Render Deployment Guide

## Overview
The fastest realistic hosted deployment path for `smb-cashflow-risk` is:
- Render PostgreSQL
- Render web service for FastAPI API
- Render web service for Next.js frontend

This is a pragmatic portfolio deploy path, not a full production hardening guide.

## Files
- `render.yaml` provides a starting blueprint for the services and database.

## Deployment steps
1. Push `main` to GitHub.
2. In Render, create a new Blueprint deployment from the repo.
3. Confirm the following resources:
   - `smb-cashflow-risk-db`
   - `smb-cashflow-risk-api`
   - `smb-cashflow-risk-web`
4. Wait for the database to provision and services to build.
5. After deploy, visit the API and web URLs.

## Required follow-up checks
- API docs reachable at `/docs`
- web dashboard loads successfully
- API/web environment variables point to the deployed API URL, not localhost

## Demo data note
This project seeds local demo data via `scripts/seed-docker.sh`.
For hosted deployment, you will need a follow-up path to load demo data into the hosted database, either by:
- temporary admin/import route usage
- one-time manual CSV import flow
- small deployment-side bootstrap script

For `v0.3.0`, a hosted deploy is preferred but not release-blocking if local Docker demo remains the primary verified path.
