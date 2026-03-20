# Portfolio Writeup

## Project
**SMB Cash Flow Risk & Invoice Default Early Warning System**

## Elevator pitch
A finance intelligence tool that helps small and mid-sized businesses spot short-term liquidity pressure, understand which receivables are most dangerous, and prioritize collection work before cash problems become operationally painful.

## Problem
SMBs often do not fail because revenue is zero. They fail because cash arrives too late. Traditional accounting reports tell you what happened; finance operators need a system that helps them decide what to do next.

## What this project demonstrates
- backend API design for an analytics product
- finance-focused feature engineering
- pragmatic forecasting and scoring baselines
- decision-oriented frontend design
- reproducible project workflow with tests and export scripts

## Core product flow
1. Load customer, invoice, payment, and cash snapshot data
2. Build invoice-level features and risk signals
3. Forecast short-term cash position
4. Rank invoices/customers by collections priority
5. Explain why an invoice is risky
6. Let a reviewer drill from summary metrics into invoice/customer detail pages

## Technical highlights
### Backend
- FastAPI
- SQLAlchemy models and ingestion pipeline
- dashboard, forecast, invoice detail, and customer detail endpoints
- portfolio ranking services driven by imported data rather than placeholder JSON

### Frontend
- Next.js app router
- dashboard summary cards
- cash forecast chart
- invoice risk queue
- invoice and customer drill-down pages
- loading, error, and empty-state handling

### Analytics baseline
- invoice-level feature builder
- `is_late_15` label definition
- rule-based baseline scoring workflow
- versioned baseline metadata + evaluation artifacts for workflow credibility
- external benchmark and native-readiness ML layers with explicit limitations

## Why it is portfolio-worthy
This project is valuable because it is not just CRUD and not just a notebook. It sits in the middle:
- product framing
- backend implementation
- analytical reasoning
- decision-support UX

That combination is closer to how real internal AI/analytics tools get built.

## What I would build next
- richer native historical data for future learned-model work
- calibration and threshold analysis once enough native evidence exists
- scenario simulation for delayed top-customer payments
- production deployment polish
- more refined frontend states and design system polish
