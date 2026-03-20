# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on Keep a Changelog and uses Semantic Versioning.

## [Unreleased]
### Added
- project-native ML readiness pipeline with honest workflow-demo deferral
- external dual-dataset benchmark pipelines
- baseline evaluation credibility layer
- Docker-based local stack and deployment notes
- CI workflow for API tests, evaluation, and web build

### Changed
- README and docs expanded to better explain ML scope, transfer decisions, and workflow
- release workflow now tracked through buildx runbooks

## [0.3.0] - 2026-03-20
### Added
- end-to-end dashboard MVP with invoice/customer detail views
- rule-based risk scoring and collections prioritization
- Dockerized local stack for reproducible demo setup
- ML credibility artifacts and benchmark pipelines
- Apache-2.0 code license

### Notes
- `v0.3.0` is the first portfolio-grade MVP release.
- Runtime scoring remains rule-based for stability and honesty.
- External learned-model pipelines are benchmark evidence, not production scoring replacements.
