# Baseline Model

## Executive summary
This project currently uses a **rule-based baseline** for receivables risk, not a trained statistical model.

That is intentional.
The current sample dataset is too small to support meaningful claims about predictive performance, so this phase focuses on **ML workflow credibility**:
- versioned baseline metadata
- deterministic evaluation plumbing
- artifact/report generation
- explicit limitations

## Model identity
- Version: `v0.1.0-rules`
- Type: `rule-based`
- Target: `is_late_15`
- Threshold: `0.50`

## Target definition
`is_late_15` means an invoice was paid 15 or more days after its due date, or remains at least 15 days overdue as of the evaluation date.

### Why this target for MVP
- easy to explain to stakeholders
- useful for collections prioritization
- simpler and more defensible than pretending to forecast exact payment dates on tiny data

## Features used
- `overdue_days`
- `payment_terms_days`
- `amount`
- `paid_ratio`
- `customer_late_invoice_ratio`

## Scoring formula
The baseline score is a heuristic weighted sum of overdue behavior, terms, exposure, payment behavior, and customer lateness history. Weights are centralized in `apps/api/app/services/model_version.py`.

## What this phase proves
This phase proves the repo has:
- a versioned baseline model definition
- deterministic split logic
- reproducible evaluation artifact generation
- explicit honesty safeguards for tiny datasets

## Known limitations
- weights are hand-picked, not learned
- scores are not calibrated probabilities
- current demo dataset is too small for meaningful metrics
- this is workflow/evaluation infrastructure, not validated predictive performance

## What would make it better
- substantially more historical invoice + payment data
- a true held-out test set
- learned baselines such as logistic regression
- calibration and threshold tuning once enough data exists
