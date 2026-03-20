# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on Keep a Changelog and uses Semantic Versioning.

## [Unreleased]
### Changed
- final release polish and release execution work in progress

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

### Changed
- README and docs expanded to explain ML scope, transfer decisions, deployment, and release/demo guidance
- runtime scoring remains rule-based for release stability and honest positioning

### Notes
- `v0.3.0` is the first portfolio-grade MVP release.
- External learned-model pipelines are benchmark evidence, not production scoring replacements.
- Project-native ML path is intentionally workflow-demo only until enough native data exists for meaningful training.
