# Demo Walkthrough

## Goal
Show the project as a polished portfolio MVP in under 3 minutes.

## Local demo path
### 1. Start services
Preferred path:
```bash
./scripts/release-demo.sh
```

Equivalent manual path:
```bash
docker compose up --build -d
sleep 10
./scripts/seed-docker.sh
```

### 2. Open the app
- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

## Talk track
### Step 1 — Dashboard overview
Explain that the dashboard is built for SMB receivables risk visibility:
- total AR
- overdue AR
- risky invoice count
- projected cash balances

### Step 2 — Risk queue
Open the invoice risk table and explain:
- rule-based risk baseline
- interpretable reason codes
- prioritization for collections work

### Step 3 — Customer detail
Open a customer page and explain:
- open exposure
- invoice history
- operational follow-up view

### Step 4 — Invoice detail
Open an invoice page and explain:
- payment history
- status
- risk bucket
- recommended action
- the new human-readable explanation of *why this invoice is risky*

### Step 5 — Honest ML framing
Explain briefly:
- runtime scoring remains rule-based for stability and honesty
- learned-model work is present as benchmark/credibility infrastructure
- native learned-model claims are intentionally deferred until enough project-native data exists

## Demo checklist
- dashboard loads cleanly
- seeded data visible
- invoice/customer pages open cleanly
- API docs reachable
- no broken empty/error states during the walkthrough
