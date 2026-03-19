# SMB Cash Flow Risk — Execution Pipeline

This project should run through a repeatable **build / buildx pipeline** under `advanced-dispatcher` so planning, implementation, testing, and review stay tight and portfolio-grade.

## 1. Outcome definition
Before writing code, confirm the slice answers all of these:
- What user/business question does this slice solve?
- What endpoint, UI element, or artifact proves it works?
- What data inputs does it require?
- What is explicitly out of scope?
- What test will fail before the work and pass after it?

## 2. Routing rule
Use one of these two tracks only:

### build — scoped slices
Use for:
- endpoint additions
- test fixes
- refactors
- docs tied to implementation
- small frontend slices
- feature engineering increments

Steps:
1. parallel-plan-a
2. parallel-plan-b
3. judge-plan
4. boilerplate
5. implement
6. test
7. simplify
8. retest
9. review-resolve
10. final-test

### buildx — major milestones
Use for:
- full frontend setup
- end-to-end dashboard build
- scoring pipeline + explanations system
- deployment + CI hardening
- major architecture changes
- ML credibility/evaluation phases with artifacts and review

Steps:
1. parallel-plan-a
2. parallel-plan-b
3. judge-plan
4. boilerplate
5. implement
6. test
7. simplify
8. retest
9. review-resolve-a
10. test-a
11. review-resolve-b
12. final-test

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
