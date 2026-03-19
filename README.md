# smb-cashflow-risk

A full-stack portfolio project for SMB cash flow risk, built with FastAPI + Next.js.

## What this project does
- score unpaid invoices for late-payment risk
- explain risk signals and recommend collections actions
- project near-term cash balances
- expose an MVP dashboard for quick review

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pydantic, pytest
- **Frontend:** Next.js / React / TypeScript
- **Infra:** Docker, docker-compose

## Quick start (Docker — recommended)
```bash
git clone https://github.com/omaression/smb-cashflow-risk.git
cd smb-cashflow-risk
docker compose up --build -d
sleep 10
./scripts/seed-docker.sh
open http://localhost:3000
```
Requires Docker and curl only — no local Python or Node.js installation needed.

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

### Demo helper
```bash
./scripts/demo.sh
```

### Export invoice features for baseline modeling
```bash
./scripts/export-invoice-features.py
# bootstraps a temporary SQLite demo DB from sample CSVs
# writes data/processed/invoice_features.csv by default
```

### Generate baseline evaluation artifacts
```bash
cd apps/api
. .venv/bin/activate
cd ../..
python scripts/evaluate-baseline.py
```
Creates workflow-demo evaluation artifacts under `artifacts/evaluations/`.

### Run external learned baselines (Phase A)
```bash
cd apps/api
. .venv/bin/activate
cd ../..
python scripts/run-external-ml-baselines.py
```
Runs separate IBM + Skywalker logistic baselines and writes comparison outputs under `artifacts/ml/`.

## Portfolio docs
- architecture tradeoffs: `docs/architecture-tradeoffs.md`
- portfolio writeup: `docs/portfolio-writeup.md`
- deployment notes: `docs/deployment-notes.md`
- baseline model: `docs/baseline-model.md`

## Reference docs
- [Execution pipeline](docs/execution-pipeline.md)
- [Milestones](docs/milestones.md)
- [Deployment notes](docs/deployment-notes.md)

## Phase plan
### Phase 0 — foundation
- define domain model
- define success metrics
- decide MVP screens
- create repo structure

### Phase 1 — data + backend baseline
- schema for customers, invoices, payments, snapshots
- CSV ingestion pipeline
- baseline risk features
- baseline cash flow forecast endpoint

### Phase 2 — scoring + explanations
- late-payment risk model
- reason codes / feature contributions
- collections priority ranking

### Phase 3 — containerization + delivery
- Dockerfile stack for reproducible deployment
- seedable demo data flow
- portfolio-ready documentation
