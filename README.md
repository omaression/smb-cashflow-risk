# smb-cashflow-risk

A full-stack portfolio project for SMB cash flow risk, built with FastAPI + Next.js.

**Live:** [cashflow.omaression.com](https://cashflow.omaression.com) &middot; **API:** [cashflow-api.omaression.com/docs](https://cashflow-api.omaression.com/docs)

## What this project does
- score unpaid invoices for late-payment risk
- explain risk signals and recommend collections actions
- project near-term cash balances
- expose an MVP dashboard for quick review
- surface ML evidence, benchmark context, and native-readiness status
- **BYOD trial workspace**: upload your own receivables data and get immediate risk insights with data-quality scoring

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pydantic, pytest
- **Frontend:** Next.js / React / TypeScript
- **Infra:** Docker, docker-compose, Vercel (frontend), VPS-hosted FastAPI, Cloudflare Tunnel/DNS

## Deployment architecture

```
cashflow.omaression.com       -> Vercel (Next.js)
cashflow-api.omaression.com   -> Cloudflare Tunnel -> VPS FastAPI
VPS PostgreSQL                -> Docker volume at /mnt/volume-1/data/smb-cashflow-risk/postgres
Cloudflare                    -> DNS + API tunnel routing
```

- **Frontend** on Vercel with automatic deploys from `main`
- **API** on VPS-hosted FastAPI behind Cloudflare Tunnel at `https://cashflow-api.omaression.com`
- **API base path** is `https://cashflow-api.omaression.com/api/v1`
- **API docs** are at `https://cashflow-api.omaression.com/docs`
- **Database** is VPS-hosted PostgreSQL in a private Docker network, persisted at `/mnt/volume-1/data/smb-cashflow-risk/postgres`
- **API to database host** is `smb-cashflow-risk-postgres` on the Docker network
- **Render docs/config** remain in-repo as legacy or backup deployment material where noted

## License
Code in this repository is licensed under **Apache-2.0**.
External datasets, benchmarks, and third-party sources may have separate licenses and usage constraints.

## Quick start (Docker, recommended)
```bash
git clone https://github.com/omaression/smb-cashflow-risk.git
cd smb-cashflow-risk
./scripts/release-demo.sh
```
Requires Docker and curl only. No local Python or Node.js installation needed.

## Local development
### API
```bash
cd apps/api
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web
```bash
cd apps/web
npm install
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev
```

## Demo commands
### One-command release demo bootstrap
```bash
./scripts/release-demo.sh
```
Builds the stack, waits for health, seeds demo data, and prints the main URLs.

### Seed a hosted deployment
```bash
./scripts/seed-remote.sh https://cashflow-api.omaression.com
```

### Release prep checks
```bash
./scripts/prepare-release.sh v0.3.0
```
Runs the key release validation steps before tagging.

### Manual demo path
```bash
docker compose up --build -d
sleep 10
./scripts/seed-docker.sh
```

## ML utility scripts
### Generate baseline evaluation artifacts
```bash
cd apps/api
. .venv/bin/activate
cd ../..
python scripts/evaluate-baseline.py
```

### Run external benchmark baselines
```bash
cd apps/api
. .venv/bin/activate
cd ../..
python scripts/run-external-ml-baselines.py
```

### Run project-native ML readiness pipeline
```bash
cd apps/api
. .venv/bin/activate
cd ../..
python scripts/run-project-native-ml-baseline.py
```
On current native sample data, this produces a workflow-demo artifact rather than claiming meaningful model training.

## Portfolio docs
- architecture tradeoffs: `docs/architecture-tradeoffs.md`
- portfolio writeup: `docs/portfolio-writeup.md`
- deployment notes: `docs/deployment-notes.md`
- current VPS/Cloudflare deploy guide: `docs/deploy-vps-cloudflare.md`
- legacy Render deploy guide: `docs/deploy-render.md`
- baseline model: `docs/baseline-model.md`
- ML project-native readiness: `docs/ml-project-native-readiness.md`
- ML transfer recommendation: `docs/ml-transfer-recommendation.md`
- release blueprint for v0.4.0 / v0.5.0: `docs/release-blueprint-v0.4.0-v0.5.0.md`

## Reference docs
- [Execution overview](docs/execution-pipeline.md)
- [Milestones](docs/milestones.md)
- [Deployment notes](docs/deployment-notes.md)
- [VPS and Cloudflare deploy guide](docs/deploy-vps-cloudflare.md)
- [Legacy Render deploy guide](docs/deploy-render.md)
- [Demo walkthrough](docs/demo-walkthrough.md)
- [Release notes](docs/release-notes-v0.3.0.md)
- [Release checklist](docs/release-checklist-v0.3.0.md)

## Phase status
### Phase 0 - foundation
- done: domain model, API contract, sample data, and repo structure established

### Phase 1 - product baseline
- done: backend API, frontend dashboard, forecasting, detail views, and rule-based scoring are in place

### Phase 2 - reliability and delivery
- done: Docker stack, deployment notes, CI, and review workflows are in place

### Phase 3 - ML credibility foundations
- done: baseline evaluation credibility layer, external benchmark pipelines, and project-native ML readiness path are in place

### Phase 4 - v0.4.0 ML credibility release
- done: ML evidence API endpoints, runtime scoring provenance in the UI, and an ML evidence page are in place
- outcome: the project now explains what is live, what is benchmark evidence, and why native learned runtime remains deferred

### Phase 5 - v0.5.0 Bring Your Own Data
- done: trial workspace foundation with isolated data scoping
- done: file-role detection for CSV/XLSX uploads (invoices, payments, customers, cash snapshots, unpaid-invoice exports)
- done: schema mapping with confidence scores and user review flow
- done: data-quality and reliability scoring with improvement recommendations
- done: `/try` upload wizard with preview and import workflow
- outcome: users can now upload their own receivables data, review detected mappings, see quality scores, and import into an isolated trial workspace for immediate risk insights

### Phase 6 - next release direction
- next: expand BYOD import capabilities and polish UX based on user feedback

## Development note
This public repo documents outcomes, usage, architecture, decisions, and limitations.
Detailed internal orchestration notes stay local and git-ignored.
