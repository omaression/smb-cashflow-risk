# Finance Project Blueprint

## One-sentence pitch
An internal finance intelligence tool that predicts short-term cash pressure, flags risky receivables, and helps SMB teams prioritize collections before liquidity becomes a problem.

## Core entities
- **Customer** — payer profile and payment behavior summary
- **Invoice** — amount, due date, status, age, payment terms
- **Payment** — payment date, amount, method, invoice mapping
- **Cash Snapshot** — daily opening/closing balance and net movement
- **Collection Action** — recommended follow-up tied to invoice/customer risk

## Primary workflows
1. Import invoice/payment/customer CSVs
2. Normalize and store records
3. Derive aging and payment-behavior features
4. Forecast short-term cash position
5. Score open invoices for late/default risk
6. Rank collection priorities
7. Display risk explanations and suggested actions

## MVP screens
1. **Overview dashboard**
   - current AR total
   - overdue amount
   - cash runway trend
   - top risky customers
2. **Invoice risk table**
   - invoice amount
   - due date
   - days overdue / days until due
   - risk score
   - explanation
3. **Customer detail**
   - historical payment behavior
   - concentration risk
   - open exposure
4. **Cash forecast**
   - 7/14/30-day projection
   - expected inflows
   - downside case

## Baseline ML/analytics approach
### Risk scoring (first pass)
Start simple before fancy:
- logistic regression or gradient-boosted tree
- target: `is_late_15` (paid or still unpaid 15+ days past due)
- features:
  - invoice amount
  - terms length
  - days since issue
  - days until due / overdue days
  - customer historical avg delay
  - customer late-payment ratio
  - invoice frequency / seasonality indicators
  - customer concentration share

### Cash forecasting (first pass)
Use a practical baseline:
- deterministic expected inflows from open invoices weighted by payment probability and expected delay
- optional time-series baseline for daily cash movement

## Design principles
- business-first, not Kaggle-first
- explanations must be readable by non-ML users
- every chart/table should support an action
- realism beats novelty

## MVP out-of-scope
- accounting system direct integrations
- multi-entity treasury management
- deep reinforcement optimization
- production-grade multi-tenant auth
- fancy streaming architecture

## Done criteria for v0
- realistic schema and seed data
- backend endpoints for ingest, dashboard summary, forecast, risk list
- frontend dashboard with clean decision-oriented views
- reproducible local setup
- concise writeup explaining product, data, models, and tradeoffs
