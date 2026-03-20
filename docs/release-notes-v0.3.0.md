# Release Notes — `v0.3.0`

## Summary
`smb-cashflow-risk` `v0.3.0` is the first **portfolio-grade MVP** release.

This release delivers a complete end-to-end demo experience for SMB receivables risk:
- FastAPI backend
- Next.js frontend
- seeded demo data
- rule-based invoice risk scoring
- collections prioritization
- Dockerized local stack
- honest ML credibility and benchmark artifacts

## Highlights
- full dashboard + invoice/customer detail flow
- reproducible local demo via Docker
- clear deployment and demo documentation
- baseline ML credibility layer with workflow-demo evaluation artifacts
- separate external benchmark pipelines for IBM and Skywalker datasets
- project-native ML readiness path that explicitly defers fake model claims on tiny native data

## What this release is
- a polished MVP for portfolio presentation
- a strong demonstration of product thinking + backend/frontend delivery + ML honesty
- a stable baseline for future improvements

## What this release is not
- not a production-hardened SaaS release
- not a claim that learned models are ready to replace the runtime scorer
- not a claim that external benchmark metrics transfer directly into production behavior

## Recommended demo path
1. start the Docker stack
2. seed the sample data
3. open the dashboard
4. walk through risk table, customer detail, invoice detail
5. explain the rule-based baseline and why the ML layers are intentionally honest about limitations

## SemVer rationale
`v0.3.0` is appropriate because the project has moved beyond rough scaffolding into a coherent, documented, demo-ready MVP with multiple substantial milestones complete.
