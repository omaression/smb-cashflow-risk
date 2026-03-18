# API Contract (v0)

## Goal
Provide enough backend surface area to support CSV ingestion, dashboard summary, invoice risk review, customer drill-down, and cash forecast views.

## Endpoints

### `POST /api/v1/import/csv`
Upload or reference CSV files for customers, invoices, payments, and optional cash snapshots.

Response:
- records imported
- records rejected
- validation errors summary

### `GET /api/v1/dashboard/summary`
Returns:
- total AR
- overdue AR
- open invoice count
- risky invoice count
- top risky customers
- 7/14/30-day projected cash balances

### `GET /api/v1/invoices/risk`
Query params:
- `status`
- `risk_bucket`
- `customer_id`
- `page`
- `page_size`
- `sort_by`

Current MVP behavior:
- returns open invoices ranked by a rule-based collections priority score
- score combines outstanding exposure, overdue severity, and late-payment probability

Each item should include:
- invoice id
- customer
- amount
- due date
- overdue days
- late-payment probability
- risk bucket
- top reason codes
- recommended action

### `GET /api/v1/invoices/{invoice_id}`
Returns invoice detail, payment history, latest score, and recommendation.

Notes:
- `invoice_id` is the external invoice id for MVP (example: `INV-1002`)
- response includes payment history, amount paid, outstanding amount, risk bucket, and recommended action

### `GET /api/v1/customers/{customer_id}`
Returns customer profile, open exposure, payment behavior summary, and open invoices.

Notes:
- `customer_id` is the external customer id for MVP (example: `CUST-001`)
- response includes open exposure, overdue counts, late-payment ratio, and open invoices with risk summary

### `GET /api/v1/forecast/cash`
Query params:
- `horizon_days` (7, 14, 30)
- `scenario` (`base`, `downside`)

Returns daily projected balances and expected inflow/outflow components.

### `GET /healthz`
Returns service health.

## Non-goals for v0
- accounting platform direct integrations
- multi-tenant user management
- writeback actions into external systems
