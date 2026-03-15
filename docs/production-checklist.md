# Production Checklist

This checklist is specific to the SMB Cash Flow Risk project.

## Data integrity
- [ ] Validate invoice/customer/payment foreign-key consistency on import
- [ ] Reject negative or impossible money values
- [ ] Reject invoices where `due_date < invoice_date`
- [ ] Recompute and verify `outstanding_amount`
- [ ] Enforce one canonical currency for MVP, or explicit FX handling before multi-currency support

## Model safety and quality
- [ ] Document training window and label definition (`is_late_15`, optional severe delinquency)
- [ ] Track model version for every score
- [ ] Measure precision/recall on high-risk bucket
- [ ] Validate calibration before showing probabilities in UI
- [ ] Keep human-readable reason codes for every surfaced prediction

## Forecast reliability
- [ ] Define forecast horizon clearly: 7/14/30 days
- [ ] Show assumptions behind expected inflows
- [ ] Distinguish booked invoices from probabilistic inflows
- [ ] Add downside case / conservative scenario
- [ ] Avoid presenting forecasts as guaranteed outcomes

## Product and UX
- [ ] Make risky invoices sortable by expected cash impact, not only probability
- [ ] Display overdue days, amount, customer exposure, and top reasons together
- [ ] Mark recommendations as decision support, not autopilot actions
- [ ] Add empty-state views with seed/demo data

## API and application ops
- [ ] Add structured logging for imports, scoring, and forecast requests
- [ ] Add health check endpoint
- [ ] Add migrations for schema changes
- [ ] Add auth before any non-demo deployment
- [ ] Add rate limits if exposed publicly

## Deployment
- [ ] Separate demo seed data from production data
- [ ] Secure environment variables and DB credentials
- [ ] Use managed Postgres backups or scheduled dumps
- [ ] Add monitoring and alerting for failed imports / model jobs
- [ ] Define retraining or rescoring cadence

## Portfolio/demo readiness
- [ ] Include a realistic walkthrough dataset
- [ ] Prepare a 2-minute demo script
- [ ] Write architecture summary and tradeoff notes
- [ ] Make local startup reproducible with one README flow
