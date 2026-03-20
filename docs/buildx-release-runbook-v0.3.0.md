# Buildx Runbook — `v0.3.0` Release

Branch: `feat/release-runbook-v1`

## Goal
Ship `smb-cashflow-risk` by tomorrow night as a **portfolio-grade MVP**:
- polished end-to-end demo
- clean docs
- honest ML framing
- release notes + changelog + SemVer tag
- public deploy preferred
- custom domain preferred but not release-blocking

## Step status
1. parallel-plan-a — DONE (`uploads/release-plan-codex.md`)
2. parallel-plan-b — DONE (`uploads/release-plan-glm5.md`)
3. judge-plan — DONE
4. blueprint — DONE
5. boilerplate — IN PROGRESS
6. implement — PENDING
7. test — PENDING
8. simplify — PENDING
9. retest — PENDING
10. review-resolve-a — PENDING
11. test-a — PENDING
12. review-resolve-b — PENDING
13. final-test — PENDING

## Judge-plan synthesis
### Release strategy
- release as **v0.3.0**
- keep runtime scoring rule-based for stability
- treat ML work as credibility/benchmark infrastructure, not production-ready predictive proof
- prioritize demo flow, docs, release artifacts, and deployability over new features

### Scope included
- release docs cleanup
- README polish
- changelog
- release notes draft
- demo walkthrough script / doc
- deployment prep and smoke checks
- final tag/release checklist

### Scope explicitly excluded
- new product features
- runtime model replacement
- deeper ML improvements
- perfectionist infra work that threatens timeline

## Release blueprint
- Create a release checklist, changelog, and release notes draft.
- Polish README/docs so a recruiter can understand the app and run the demo quickly.
- Strengthen the demo path so seeded local or hosted usage feels smooth and intentional.
- Prepare deployment notes for a hosted release; use provider URLs if custom domain setup drags.
- Run final validation across API tests, web build, Docker stack, and seeded demo flow.
- Merge release-polish changes.
- Tag and publish `v0.3.0` with clear release notes.

## Time-slip cut list
If time slips, cut in this order:
1. custom domain setup
2. cosmetic UI polish beyond obvious issues
3. extra release-note embellishment
4. deployment extras beyond one stable hosted URL

Do **not** cut:
- changelog
- release notes
- final smoke tests
- demo flow clarity
- honest docs

## Done criteria by tomorrow night
- repo main is clean and documented
- changelog exists
- release notes are ready
- release tag chosen and checklist complete
- demo path is obvious and tested
- hosted deploy exists if feasible; provider URL acceptable if domain not finished
ain not finished
