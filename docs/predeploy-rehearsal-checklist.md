# Pre-Deployment Rehearsal — `v0.3.0`

Use this runbook first thing before tomorrow's release window. It validates the exact paths you will rely on during deployment.

## 1) Fresh local rehearsal environment (5–10 minutes)
- `git checkout main`
- `git pull --ff-only`
- `git status --short` (expect clean)
- `docker compose down` (cleanup leftover containers/networks)
- `./scripts/predeploy-rehearsal.sh`

## 2) Validate core runtime (`./scripts/predeploy-rehearsal.sh`)
- API health returns `200` on `/healthz`
- Dashboard API endpoint returns JSON with:
  - `open_invoice_count`
  - `projects_total`
  - `risk_distribution`
- Demo pages return non-error HTML:
  - `http://localhost:3000`
  - `http://localhost:3000/invoices/<sample-invoice-id>`
  - `http://localhost:3000/customers/<sample-customer-id>`
- API docs loads at `http://localhost:8000/docs`

## 3) Verify pre-release checks
- `./scripts/prepare-release.sh v0.3.0`
  - Must pass all 6 steps
  - Confirm generated artifacts appear under `artifacts/`
- If any step fails, fix immediately and re-run from the failed section

## 4) Capture deployment evidence
- copy successful command log/outputs for:
  - API health
  - web/build smoke
  - `prepare-release.sh` success
- note timestamp + timezone

## 5) Final deployment gates
- `CHANGELOG.md` and `docs/release-notes-v0.3.0.md` finalized
- `docs/release-checklist-v0.3.0.md` blockers complete
- tag is ready (`v0.3.0`)

## 6) 60-second rollback plan
- Keep `scripts/release-demo.sh` output bookmarked
- if deployment smoke fails, revert to latest working deployment and post-mortem in issue

## Notes
- This script is intended for local rehearsal only.
- Use the hosted URLs only after successful local rehearsal and final DNS/environment wiring decisions.
