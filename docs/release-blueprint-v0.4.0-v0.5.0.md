# Release Blueprint — v0.4.0 and v0.5.0

## Purpose
This document defines the public implementation blueprint for the next two releases of `smb-cashflow-risk`.

- **v0.4.0** focuses on **ML credibility**
- **v0.5.0** focuses on a **bring-your-own-data trial flow**

The guiding principle is honesty:
- do not overclaim ML maturity
- do not present benchmark results as runtime proof
- do not add fake SaaS complexity before the product earns it

---

# v0.4.0 — ML credibility release

## Release goal
Make the project’s ML story inspectable and credible without replacing the current runtime rule-based scorer.

A reviewer should be able to answer:
- what powers runtime scoring today
- what experimental ML evidence exists
- why project-native learned runtime is still deferred
- what conditions would unlock future native learned runtime scoring

## Product outcome
The app should clearly communicate:
- **Runtime scorer:** rule-based baseline
- **External ML:** benchmark evidence only
- **Project-native ML:** currently deferred until sufficient data exists

## In scope
- new ML evidence API endpoints
- ML evidence page in the web app
- runtime scoring provenance in dashboard/detail views
- native-readiness status surfaced from existing artifacts/config
- benchmark comparison summaries surfaced from existing artifacts/docs
- release-safe tests around ML honesty and artifact handling

## Out of scope
- replacing the runtime scorer with a learned model
- in-app training controls
- scheduled retraining infrastructure
- deep experiment tracking platform
- tenant-specific ML behavior

## Backend blueprint

### New router
Add:
- `apps/api/app/routers/ml.py`

Register routes for:
- `GET /api/v1/ml/overview`
- `GET /api/v1/ml/models`
- `GET /api/v1/ml/models/{model_version}`
- `GET /api/v1/ml/benchmarks`
- `GET /api/v1/ml/native-readiness`

### New services
Add:
- `apps/api/app/services/ml_artifacts.py`
- `apps/api/app/services/ml_registry.py`
- `apps/api/app/services/ml_readiness.py`

Responsibilities:
- scan and normalize artifact data from `artifacts/ml/` and `artifacts/evaluations/`
- expose runtime model metadata from the existing scoring/model-version path
- centralize native readiness threshold logic and caveat text
- provide API-safe summary objects for the web app

### Existing route enrichment
Optionally extend:
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/invoices/{invoice_id}``

Suggested added fields:
- `runtime_model_version`
- `score_type`
- `ml_status_badge`

These fields should be informational only and must not alter runtime scoring behavior.

## API contract

### `GET /api/v1/ml/overview`
Returns a compact high-level ML status payload:
- `runtime_model`
- `native_pipeline`
- `external_benchmarks`
- `transfer_recommendation`

### `GET /api/v1/ml/models`
Returns a list of:
- runtime model metadata
- benchmark artifact entries
- native artifact entries, if present

### `GET /api/v1/ml/models/{model_version}`
Returns a model card containing:
- model identity
- target
- model family / scoring type
- feature family
- metric summary
- limitations
- provenance
- runtime approval status

### `GET /api/v1/ml/benchmarks`
Returns benchmark summaries with:
- dataset identifier
- sample size / label ratio where available
- validation strategy
- headline metrics
- caveats
- non-transferability warning

### `GET /api/v1/ml/native-readiness`
Returns:
- row count
- positive count
- configured minimum thresholds
- readiness verdict
- blocker summary
- next unlock condition

## Frontend blueprint

### New page
Add:
- `apps/web/app/ml/page.tsx`

This page should include:
1. **Runtime scorer card**
2. **Project-native readiness panel**
3. **External benchmark comparison section**
4. **What transfers / what does not**
5. **Links to supporting artifacts/docs**

### New components
Add components such as:
- `ml-overview-card.tsx`
- `model-card.tsx`
- `benchmark-comparison-table.tsx`
- `native-readiness-panel.tsx`
- `honesty-callout.tsx`

### Dashboard tweaks
Add a lightweight path into the ML story:
- `ML evidence` chip/link
- compact status card for runtime / benchmark / native status

### Invoice detail tweaks
Display explicit provenance:
- model version
- score type (`rule-based baseline`)
- optional link to ML evidence page

## Data and persistence approach
For `v0.4.0`, prefer **no required schema migration**.

Use:
- existing runtime scoring metadata
- existing ML artifacts on disk
- existing readiness rules/config

Do not add a model registry table unless artifact discovery becomes unmanageable.

## Tests

### Backend
Add tests for:
- ML overview endpoint
- benchmark endpoint
- native-readiness endpoint
- missing/partial artifact handling
- deterministic caveat fields

### Frontend
Verify:
- `/ml` renders without artifacts crashing the page
- benchmark warnings render clearly
- invoice/detail provenance copy appears

### Release checks
- seeded demo still works unchanged
- runtime scoring output remains stable
- web build passes
- public ML wording matches the docs

## Done criteria
`v0.4.0` is done when a reviewer can inspect the app and understand the ML story without guessing.

---

# v0.5.0 — Bring-your-own-data trial flow

## Release goal
Let a user trial the product with their own invoice/customer/payment CSV exports through a guided web flow instead of raw API calls.

## Product outcome
A user should be able to:
1. download templates
2. upload CSV files
3. preview validation results
4. import into a trial dataset
5. view dashboard, invoice risk, and detail pages for that uploaded dataset

## In scope
- CSV template guidance
- upload + preview validation flow
- dataset-scoped import path
- dataset-scoped dashboard/risk/detail views
- user-friendly validation messages
- explicit warnings about small or incomplete datasets

## Out of scope
- accounting integrations
- user accounts / organizations
- permanent hosted file storage guarantees
- automatic model training on upload
- production multi-tenant data isolation platform

## Backend blueprint

### Evolve ingestion APIs
Add or extend endpoints for:
- `POST /api/v1/import/csv/preview`
- `POST /api/v1/import/csv`
- `GET /api/v1/trial/{dataset_id}/status`
- `GET /api/v1/trial/{dataset_id}/summary`
- `GET /api/v1/trial/{dataset_id}/invoices/risk`
- `GET /api/v1/trial/{dataset_id}/customers/{customer_id}`
- `GET /api/v1/trial/{dataset_id}/invoices/{invoice_id}`

### New services
Add service modules such as:
- `import_preview.py`
- `import_validation.py`
- `trial_workspace.py`
- `workspace_portfolio.py`

Responsibilities:
- file-role detection
- schema validation
- preview statistics
- plain-language error reporting
- trial dataset creation/replacement
- workspace-scoped reads for dashboard and drilldown pages

## Data model direction
Introduce a lightweight trial-scoping concept.

Minimal viable approach:
- `trial_workspace`
  - `id`
  - `created_at`
  - `label`
  - `status`
- imported records associated to `workspace_id`

Key requirement:
- seeded demo data must remain separate from trial-uploaded data
- one active trial dataset at a time is acceptable for this release if it keeps the architecture clean

## Frontend blueprint

### New page
Add:
- `apps/web/app/try/page.tsx`

Flow:
1. download templates
2. upload files
3. preview + fix issues
4. import dataset
5. open results

### New components
Add components such as:
- `upload-wizard.tsx`
- `csv-template-downloads.tsx`
- `validation-summary.tsx`
- `import-preview-table.tsx`
- `dataset-status-banner.tsx`

### UX requirements
Validation must be plain-language and actionable, for example:
- missing required column `invoice_id`
- invalid date format in `due_date`
- duplicate invoice IDs found
- payment references unknown invoice

### Post-import UX
After successful import, the app should clearly show:
- imported row counts
- warnings
- which dataset is active
- whether native ML remains deferred for the uploaded data

## Tests

### Backend
Add tests for:
- preview validation happy path
- missing columns
- malformed dates
- duplicate IDs
- unknown invoice references
- workspace-scoped summary/risk/detail reads

### Frontend
Verify:
- upload flow states
- validation summary rendering
- import success path
- dataset status banner rendering
- fallback/empty/error states

### Release checks
- demo mode still works
- trial flow works end-to-end with sample CSVs
- invalid CSVs fail gracefully
- imported data does not leak into demo mode

## Done criteria
`v0.5.0` is done when a new user can try the product with their own CSV exports without needing to call the API manually.

---

# Release sequencing

## Recommended order
1. Finish `v0.4.0` first
2. Ship ML credibility before widening ingestion UX
3. Use `v0.4.0` artifact/status contracts as part of `v0.5.0` trial messaging

## Rationale
If the product becomes easier to try before the ML story is credible, the app still risks feeling like a slick wrapper around static demo logic.

---

# Clean repo rules for this roadmap
- Keep public docs focused on product behavior, architecture, usage, limitations, and release scope
- Keep internal orchestration details out of public docs
- Keep Git-visible diffs scoped to one release slice at a time
- Avoid speculative infra and unused abstractions
- Prefer file-local clarity over sprawling helper layers unless repetition proves the need
