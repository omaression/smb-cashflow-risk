# Architecture Tradeoffs

## Why this project is structured as a backend + dashboard + baseline analytics stack
The goal is not to win a Kaggle competition. The goal is to show strong product judgment for a finance workflow:
- ingest messy operational data
- derive business-readable signals
- rank work that a finance team can actually act on
- explain why the system is worried

That led to a deliberately practical architecture.

## 1. FastAPI over a heavier backend framework
**Chosen:** FastAPI

**Why it won:**
- fast to scaffold for portfolio work
- clean schema-first API design
- good fit for lightweight analytics services
- easy to pair with Pydantic for response contracts

**Tradeoff:**
- less batteries-included than a larger framework
- if the project grew into multi-tenant auth/admin workflows, more structure would be needed

## 2. Deterministic baseline forecast before time-series sophistication
**Chosen:** deterministic invoice-weighted cash forecast

**Why it won:**
- easier to explain to non-ML reviewers
- directly tied to open receivables and payment assumptions
- good enough to demonstrate product value quickly

**Tradeoff:**
- less expressive than a full statistical forecasting pipeline
- depends on heuristic assumptions instead of learned dynamics

## 3. Rule-based risk baseline before model training
**Chosen:** engineered features + baseline rule scorer

**Why it won:**
- gives the project real scoring behavior early
- creates a clear bridge to a later learned model
- avoids pretending the current tiny dataset can justify serious training claims

**Tradeoff:**
- weaker than a trained model on real historical data
- score calibration is heuristic, not learned

## 4. SQLite bootstrapping for demo scripts instead of requiring live Postgres
**Chosen:** temporary SQLite for feature export helper

**Why it won:**
- lowers friction for reviewers and local demos
- avoids requiring infrastructure just to validate portfolio artifacts
- keeps the scripted workflow reproducible from sample CSVs alone

**Tradeoff:**
- not a full substitute for validating the production-target database path
- Postgres-specific behavior still needs explicit environment testing later

## 5. Decision-oriented UI over pixel-heavy dashboards
**Chosen:** simple cards, ranked tables, drill-down pages

**Why it won:**
- makes the business case legible quickly
- lets reviewers follow the decision path from summary → invoice/customer detail
- prioritizes signal over flashy visuals

**Tradeoff:**
- less visually differentiated than a highly polished analytics product
- more UX refinement is still needed for empty/error/loading states and final polish

## Next tradeoffs to resolve
1. whether to add a lightweight trained model now or wait for richer synthetic/historical data
2. whether to expose feature/scoring artifacts through API endpoints or keep them script-first
3. whether to containerize immediately or finish docs/polish first
