# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on Keep a Changelog and uses Semantic Versioning.

## [0.3.0] - 2026-03-20
### Added
- end-to-end dashboard MVP with invoice/customer detail views
- rule-based risk scoring and collections prioritization
- Dockerized local stack for reproducible demo setup
- one-command release demo bootstrap via `scripts/release-demo.sh`
- baseline evaluation credibility layer
- external benchmark pipelines for IBM and Skywalker datasets
- project-native ML readiness pipeline with honest workflow-demo deferral
- CI workflow for API tests, evaluation, and web build
- deployment prep via `render.yaml` and `docs/deploy-render.md`
- Apache-2.0 code license
- release notes, demo walkthrough, and release checklist docs
- CORS middleware with configurable `ALLOWED_ORIGINS`
- Vercel deployment config for Next.js frontend
- remote seeding script (`scripts/seed-remote.sh`) for hosted deploys
- SVG favicon and Open Graph metadata for portfolio sharing
- footer branding with link to omaression.com

### Changed
- README and docs expanded to explain ML scope, transfer decisions, deployment, and release/demo guidance
- runtime scoring remains rule-based for release stability and honest positioning
- top risky customers API now returns `{id, name}` objects for proper frontend linking
- removed hardcoded sample customer lookup in frontend
- cleaned demo-specific language from UI copy
- empty-state component accepts contextual kicker text
- cash forecast chart shows value labels on bars with aria attributes
- render.yaml updated for Vercel + Render split deployment (Render web kept as backup)
- deployment architecture: Vercel (frontend) + Render (API + Postgres) + Cloudflare DNS

### Notes
- `v0.3.0` is the first portfolio-grade MVP release.
- External learned-model pipelines are benchmark evidence, not production scoring replacements.
- Project-native ML path is intentionally workflow-demo only until enough native data exists for meaningful training.
