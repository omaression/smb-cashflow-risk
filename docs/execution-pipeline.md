# SMB Cash Flow Risk — Execution Pipeline

This project should run through `advanced-dispatcher` workflows so planning, implementation, testing, and review stay tight and portfolio-grade.

## How the workflow works
All dispatcher workflows (`buildq`, `build`, `buildx`) should follow the same overall pattern:
- parallel planning from at least two perspectives
- judge-plan synthesis
- a mandatory **blueprint** before any boilerplate or implementation work
- implementation + testing
- simplification + retesting
- review-driven fixes
- final validation before merge

### Blueprint rule
- `build` and `buildx` should generate the blueprint with **`gpt-5.4`**
- `buildq` should generate the blueprint with **`gpt-5.3-codex`**
- the blueprint should be explicit enough that implementation is executing a concrete plan, not improvising

## Outcome definition
Before writing code, confirm the slice answers all of these:
- What user/business question does this slice solve?
- What endpoint, UI element, or artifact proves it works?
- What data inputs does it require?
- What is explicitly out of scope?
- What test will fail before the work and pass after it?

## Routing rule
### `build`
Use for scoped slices such as:
- endpoint additions
- test fixes
- refactors
- docs tied to implementation
- small frontend slices
- feature engineering increments

### `buildx`
Use for major milestones such as:
- end-to-end product phases
- deployment / CI hardening
- architecture changes
- ML credibility or evaluation phases with artifacts and review

## Current expectation
The workflow is only considered complete when implementation, tests, review fixes, and final validation have all been executed — not just the planning and review lanes.

## 3. Master delivery checklist

### Foundation / repo hygiene
- [x] Separate project repo exists under `projects/`
- [x] README explains the product clearly
- [x] Blueprint, domain model, and API contract exist
- [x] Initial SQL schema exists
- [ ] Exact backend package layout finalized
- [ ] Exact frontend app layout finalized
- [ ] CI/test command documented at repo root
- [ ] Demo walkthrough script written

### Data layer
- [x] Sample customers CSV
- [x] Sample invoices CSV
- [x] Sample payments CSV
- [x] Sample cash snapshots CSV
- [x] CSV validators and ingestion path
- [x] Processed demo dataset generation script
- [x] Feature dataset builder for modeling
- [ ] Data quality checks for missing/invalid finance records

### Backend API
- [x] Health endpoint
- [x] Dashboard summary endpoint
- [x] Invoice risk list endpoint
- [x] CSV import endpoint
- [x] Cash forecast endpoint contract defined
- [x] Cash forecast endpoint implemented against data logic
- [ ] Invoice detail endpoint
- [ ] Customer detail endpoint
- [ ] Shared service layer for summary/risk/forecast logic
- [ ] Stable response fixtures/examples for docs

### Analytics / ML
- [x] Baseline receivables feature engineering
- [x] Label definition script for `is_late_15`
- [x] Rule-based or baseline probability scorer
- [x] Reason-code generation
- [x] Collection priority ranking formula
- [ ] Evaluation notebook or report
- [ ] Model versioning conventions

### Frontend
- [x] Next.js app scaffolded
- [x] Dashboard shell and layout
- [x] Summary cards wired to API
- [x] Invoice risk table wired to API
- [x] Cash forecast chart wired to API
- [x] Customer detail page
- [x] Invoice detail page
- [ ] Empty/loading/error states
- [ ] Portfolio-ready visual polish

### Quality / ops
- [x] Test harness runs cleanly from repo commands
- [x] API tests cover happy path + bad inputs
- [x] Forecast tests validate business logic
- [x] Basic frontend smoke tests
- [x] Docker/dev environment documented
- [x] Deployment notes added
- [x] Portfolio writeup added

## 4. Slice-by-slice pipeline template
Copy this for each task:

## Slice: <name>
**Goal:**
**User-visible artifact:**
**Inputs:**
**Out of scope:**

### Plan
- [ ] confirm contract
- [ ] identify touched files
- [ ] define test cases

### Implement
- [ ] add/modify code
- [ ] keep diff minimal
- [ ] avoid speculative abstractions

### Test
- [ ] run targeted tests
- [ ] run broader suite if shared code changed

### Simplify
- [ ] remove dead code
- [ ] collapse unnecessary indirection
- [ ] keep naming/business semantics clear

### Review
- [ ] verify contract matches docs
- [ ] verify portfolio story is stronger after change
- [ ] update milestone/docs only if needed

## 5. Ordered work queue

### Active now
1. **Backend cash forecast slice**
   - implement `GET /api/v1/forecast/cash`
   - add deterministic forecast logic based on seeded data
   - add API tests
   - fix any broken test harness setup

### Next
2. **Backend detail endpoints**
   - invoice detail
   - customer detail
3. **Risk scoring baseline**
   - feature engineering
   - initial rule/model score
   - reason codes
4. **Frontend baseline**
   - Next.js scaffold
   - dashboard shell
   - summary/risk/forecast views
5. **Portfolio polish**
   - demo script
   - deployment notes
   - polished writeup

### Recently completed
- Backend cash forecast
- Backend detail endpoints
- Frontend dashboard shell
- Frontend customer detail page
- Rule-based receivables ranking and dashboard summary services

## 6. Done criteria for each slice
A slice is done only when:
- tests pass
- docs and code do not contradict each other
- the change improves the demo story
- the diff stays tight and understandable
- the next slice is clearer because of this one

## 7. Current slice status
**Completed slice:** Backend cash forecast

Checklist:
- [x] identify missing endpoint and contract
- [x] implement forecast service
- [x] add forecast router
- [x] add schema models for forecast response
- [x] fix test import path issues
- [x] add forecast tests
- [x] run backend pytest cleanly

**Next recommended slice:** Invoice detail + customer detail endpoints
] run backend pytest cleanly

**Next recommended slice:** Invoice detail + customer detail endpoints
