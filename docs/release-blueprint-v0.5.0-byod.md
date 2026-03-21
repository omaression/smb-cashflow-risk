# Release Blueprint — v0.5.0 Bring Your Own Data

## Purpose
This document defines the public implementation blueprint for `v0.5.0` of `smb-cashflow-risk`.

The release goal is to turn the product from a fixed demo-data experience into a guided bring-your-own-data workflow that can ingest messy receivables data, normalize it into a trustworthy canonical model, and surface late-payment risk, cash forecast, and reliability guidance without overclaiming model maturity.

---

# Product stance

## What v0.5.0 should confidently do
- accept messy receivables exports through a guided upload workflow
- infer likely file roles and likely column mappings
- let the user review or override ambiguous mappings
- normalize uploaded records into a canonical receivables model
- validate and reconcile records before import
- score open invoices using the current runtime baseline
- project near-term cash balances with deterministic logic
- surface confidence and data-quality factors for all major outputs
- recommend concrete steps that would improve reliability in the next upload

## What v0.5.0 should not claim
- perfect handling of every spreadsheet shape
- automatic model training on arbitrary uploads
- direct transfer of benchmark ML results into company-specific runtime predictions
- enterprise-grade ERP integration
- a full multi-tenant SaaS onboarding platform

---

# Release goal

A user should be able to:
1. open `/try`
2. upload one or more messy CSV/XLSX files
3. review detected file roles and column mappings
4. preview validation results and data-quality issues
5. import into an isolated trial workspace
6. view dashboard, invoice risk queue, invoice/customer detail, and forecast for that uploaded dataset
7. understand how trustworthy the outputs are and what changes would improve reliability

---

# Core architecture

## Recommended flow

Upload
→ parse safely
→ profile raw columns
→ detect file role
→ infer schema mapping
→ normalize into canonical staging rows
→ validate and reconcile
→ compute data-quality and sufficiency factors
→ import into workspace-scoped entities
→ run scoring and forecast
→ compose confidence/reliability outputs
→ provide user recommendations

## Trial workspace requirement
The release must introduce trial dataset isolation.

### New concept
`trial_workspace`
- unique id
- status
- source type
- timestamps
- quality/confidence summary

### Workspace scoping
Add `workspace_id` to imported business entities:
- customers
- invoices
- payments
- cash snapshots

This keeps demo data and uploaded data fully separate.

---

# Ingestion architecture

## New ingestion layers
The current fixed-schema import path should be expanded into explicit layers.

### 1. File intake
Responsibilities:
- safe file acceptance
- encoding handling
- CSV/XLSX parsing
- original-file preservation
- parse warnings

### 2. File-role detection
Supported roles:
- invoices
- payments
- customers
- cash snapshots
- unpaid invoice export shortcut

Detection signals:
- filename hints
- header similarity
- value shape
- presence of signature fields

### 3. Schema inference and mapping
Responsibilities:
- normalize headers
- infer canonical fields from aliases and value patterns
- assign confidence per inferred mapping
- support user overrides before import

### 4. Normalization
Responsibilities:
- parse dates from common formats
- parse currency and amount values
- normalize statuses and booleans
- derive safe fallback values when possible
- preserve row lineage back to source file and source row

### 5. Validation and reconciliation
Two levels:
- row-level checks
- dataset-level consistency checks

### 6. Preview summarization
Responsibilities:
- import-readiness summary
- issue counts by severity
- data-quality factor summary
- actionable recommendations

### 7. Import materialization
Responsibilities:
- create workspace
- write normalized records into workspace-scoped tables
- persist quality profile and import metadata
- fail atomically when import cannot safely proceed

---

# Canonical model

## Core entities stay stable
Keep the domain model small and explicit:
- customer
- invoice
- payment
- daily_cash_snapshot

## Minimum invoice data for useful scoring
Required minimum fields:
- invoice identifier
- invoice date
- due date
- amount or outstanding amount
- customer linkage (id or resolvable name)

## Single-file unpaid-invoice support
This release should support a common SMB shortcut:
- one unpaid-invoice export only

In that path, the app may:
- generate customer records from invoice-level input
- run invoice scoring
- run a downgraded forecast with reduced confidence
- clearly show missing payment/cash-history limitations

---

# Validation and issue model

## Severity classes
- fatal
- high
- medium
- low

## Issue categories
- mapping ambiguity
- missing required fields
- type/format errors
- temporal inconsistency
- amount inconsistency
- status inconsistency
- duplicate/conflict
- stale data
- low history depth
- low payment observability
- customer identity fragmentation

## Example checks
- due date before invoice date
- duplicate invoice ids with conflicting totals
- payment before invoice date
- open amount exceeding total amount
- payment references unknown invoice
- no open invoices in a file claimed to be unpaid invoices
- missing due dates for too many rows
- snapshot too stale for credible forecast confidence

## User-facing output
Every preview/import should provide:
- issue summary
- issue counts by severity
- downloadable row-level issue report
- top recommendations for improvement

---

# Confidence and reliability model

## Design principle
Do not present a single fake “accuracy” number.

Instead, compute three separate factors:

### 1. Data quality confidence
Based on:
- required-field coverage
- mapping certainty
- validation pass rate
- duplicates/conflicts
- freshness
- payment observability
- customer identity quality

### 2. Model applicability confidence
Based on:
- sufficiency thresholds
- history depth
- feature availability
- portfolio composition support
- fallback usage

### 3. Predictive confidence
Based on:
- score stability
- calibration state where available
- forecast interval width or scenario spread
- variance under data perturbation or weak-support conditions

## User-facing rollup
Expose:
- `Reliability: High / Moderate / Low / Insufficient`
- top reasons
- top improvements that would likely increase reliability next time

---

# Scoring and forecast approach

## Risk scoring
For `v0.5.0`, keep the current runtime baseline as the always-available scoring path.

The system may enrich outputs with stronger confidence logic, but should not claim learned model calibration from arbitrary user uploads.

## Cash forecast
Keep the forecast deterministic and scenario-based.

Degrade reliability when key supporting data is weak or missing, such as:
- stale cash snapshots
- no payment history
- poor outstanding balance coverage

---

# API blueprint

## Preview/import APIs
Suggested endpoints:
- `POST /api/v1/import/preview`
- `POST /api/v1/import/preview/{preview_id}/confirm`
- `POST /api/v1/import/preview/{preview_id}/materialize`
- `GET /api/v1/trial/{workspace_id}/status`
- `GET /api/v1/trial/{workspace_id}/quality`
- `GET /api/v1/trial/{workspace_id}/summary`
- `GET /api/v1/trial/{workspace_id}/invoices/risk`
- `GET /api/v1/trial/{workspace_id}/invoices/{invoice_id}`
- `GET /api/v1/trial/{workspace_id}/customers/{customer_id}`
- `GET /api/v1/trial/{workspace_id}/forecast`

## Preview contract should include
- detected file roles
- mapping suggestions and confidence
- validation issues
- estimated imported counts
- quality/confidence preview
- recommendations before import

---

# Frontend blueprint

## New route
`/try`

## UX flow
### Step 1 — upload
- drag/drop or file picker
- file status cards
- role detection summary

### Step 2 — mapping review
- detected columns
- inferred canonical fields
- confidence indicators
- user overrides

### Step 3 — validation preview
- issue summary by severity
- import readiness banner
- confidence preview
- recommendations

### Step 4 — import
- materialize into trial workspace

### Step 5 — results
- dashboard
- invoice risk queue
- forecast
- reliability summary
- recommendations panel

## UX standard
The product should never say only “invalid file.”
It should explain:
- what it recognized
- what it could not trust
- what still works
- what reduced reliability
- what to improve next

---

# Multi-PR release slicing

## PR 1 — trial workspace foundation
- workspace schema
- workspace scoping in entities/queries
- import job metadata

## PR 2 — role detection and mapping
- file-role detection
- alias dictionaries
- mapping engine
- mapping review contract

## PR 3 — normalization and validation
- canonical normalization
- validation rules
- issue taxonomy
- preview summary generation

## PR 4 — quality/confidence layer
- data-quality scoring
- reliability composition
- recommendations engine

## PR 5 — `/try` UX flow
- upload
- mapping review
- validation preview
- import path

## PR 6 — workspace-scoped results and polish
- results pages wired to imported workspaces
- confidence surfaced in result views
- docs and UX polish

---

# Scope boundaries

## In scope
- messy upload handling
- schema inference and user-confirmed mapping
- normalization and validation
- workspace isolation
- rule-based scoring and deterministic forecast on uploaded data
- reliability/confidence reporting
- improvement recommendations

## Out of scope
- automatic model training from uploads
- ERP integrations
- full multi-tenant auth platform
- enterprise-grade master data resolution
- replacing runtime scoring with a learned model in this release

---

# Done criteria
`v0.5.0` is done when a user can upload messy unpaid-invoice data, get useful outputs, and understand:
1. what the system inferred
2. what it trusts
3. how much to trust the outputs
4. what to fix to improve reliability next time
