# Release Guide — `v0.3.0`

## Goal
Ship `smb-cashflow-risk` as a **portfolio-grade MVP** with:
- a polished end-to-end demo
- clean docs
- honest ML framing
- release notes + changelog + SemVer tag
- a public deploy if feasible within the release window

## Release strategy
For `v0.3.0`, the product should optimize for:
- stability over feature creep
- demo clarity over extra surface area
- honest ML positioning over exaggerated model claims
- strong documentation over internal process visibility

Runtime scoring should remain rule-based for this release.
The ML layers should be presented as credibility and benchmark infrastructure, not as production-ready scoring replacements.

## Included in this release
- release docs cleanup
- README polish
- changelog
- release notes draft
- demo walkthrough
- deployment prep and smoke checks
- final release checklist

## Explicitly out of scope
- new product features
- runtime model replacement
- deeper ML improvements
- nonessential infrastructure work that threatens the timeline

## Release blueprint
- finalize changelog and release notes
- polish README/docs for recruiter readability
- make the demo path smooth and obvious
- verify Docker + seed + app smoke flow
- attempt a public deploy if practical
- tag and publish `v0.3.0`

## Time-slip cut list
If time slips, cut in this order:
1. custom domain setup
2. extra cosmetic polish beyond obvious cleanup
3. release-note embellishment
4. deployment extras beyond one stable public URL

Do **not** cut:
- changelog
- release notes
- final smoke tests
- demo flow clarity
- honest docs

## Done criteria
This release is ready when:
- `main` is clean and documented
- changelog and release notes are finalized
- demo path is tested and clear
- final smoke checks pass
- `v0.3.0` is tagged and published
- a hosted demo exists if feasible, with provider URL acceptable if custom domain is not finished
