# SMB Cash Flow Risk & Invoice Default Early Warning System

A portfolio project for small and medium-sized businesses that need early visibility into cash flow volatility, receivables risk, and likely late or defaulting invoices.

## Problem
SMBs often get hurt by delayed receivables and weak liquidity visibility before traditional accounting metrics make the danger obvious.

This project aims to help finance teams answer:
- What will cash position look like over the next 7, 14, and 30 days?
- Which invoices are most likely to be paid late?
- Which customers are driving liquidity risk?
- What actions should the team prioritize today?

## Target users
- founders and operators at SMBs
- finance managers / controllers
- accounts receivable teams
- fractional CFOs

## MVP
The MVP will:
1. ingest invoice, payment, customer, and account data
2. compute receivables and payment behavior features
3. forecast short-term cash flow
4. score late-payment risk for open invoices
5. rank collection priorities
6. explain why an invoice or customer is risky
7. show the results in a clean dashboard

## Stretch goals
- scenario simulation ("what if top customer pays 10 days late?")
- intervention recommendation engine
- customer segmentation by payment behavior
- anomaly detection on receivables patterns
- alerting for liquidity thresholds

## Proposed stack
- **Backend:** FastAPI, Python 3.12
- **Database:** PostgreSQL
- **Frontend:** Next.js / React / TypeScript
- **ML / Analytics:** pandas, scikit-learn, XGBoost or LightGBM, SHAP, statsmodels / baseline forecasting
- **Infra:** Docker, docker-compose

## MVP architecture
- `apps/api` — API, feature pipelines, model serving, business logic
- `apps/web` — dashboard UI
- `data` — sample datasets and generated artifacts
- `docs` — architecture, milestones, product notes
- `sql` — schema and seed scripts

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

### Phase 3 — dashboard
- portfolio overview
- customer risk table
- invoice risk detail
- cash forecast chart

### Phase 4 — polish
- tests
- demo seed data
- metrics and writeup
- deployment

## Initial success criteria
A reviewer should be able to:
- load sample SMB finance data
- see a forecast for short-term cash position
- see ranked risky invoices/customers
- understand why the model flagged them
- understand the business value in under 2 minutes

## Portfolio docs
- architecture tradeoffs: `docs/architecture-tradeoffs.md`
- portfolio writeup: `docs/portfolio-writeup.md`
