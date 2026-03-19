# ML Transfer Recommendation

## Executive decision
Do **not** replace the current in-app rule-based scorer with either external-data model yet.

Instead, treat the two learned pipelines as **benchmark and feature-discovery tools**, then selectively transfer only the parts that improve `smb-cashflow-risk` without overstating confidence.

## Why not replace the scorer yet?
Even though the external baselines performed well:
- IBM logistic baseline F1: `0.6182`
- Skywalker logistic baseline F1: `0.9495`

those metrics are on **external invoice datasets**, not on the project’s native demo data or real project users.

### Main reason to hold back
A high metric on an external dataset is **not** the same as validated project fit.

Specific concerns:
- provenance of the datasets is weaker than first-party operational data
- target definitions are externally derived
- some source columns are unusually close to the eventual payment outcome
- the Skywalker result is especially strong, which raises the bar for skepticism even though leakage controls were added

## What should transfer into smb-cashflow-risk now
### 1. Keep the current rule-based scorer as the app default
Reason:
- already integrated
- interpretable
- honest relative to available in-project data
- safer than pretending the external learned model is production-ready

### 2. Transfer feature ideas, not the full learned model
Adopt these concepts into the project roadmap:
- stronger temporal split discipline for any future learned model work
- explicit threshold selection on validation, then test-only reporting
- better separation between training artifacts and app scoring logic
- larger emphasis on class imbalance handling

### 3. Use IBM as the more conservative benchmark reference
IBM is the better **credibility anchor** even though it scores worse than Skywalker.

Why:
- smaller and less flashy
- easier to explain
- more believable as a sanity benchmark
- lower risk of accidental overclaiming

### 4. Use Skywalker as a stress-test / upper-bound reference only
Skywalker is valuable, but should currently be treated as:
- a strong benchmark
- a source of feature ideas
- a sign that the pipeline can learn signal at scale

Not as:
- immediate production model candidate
- proof that `smb-cashflow-risk` is now ML-validated

## Recommended next implementation phase
### Phase B — project-fit learned baseline
Build a **project-native learned baseline** using the current feature-builder and project schema, even if the dataset is still limited.

Goal:
- train a logistic model on the project’s own normalized feature table
- compare it against the rule-based scorer
- keep the same honesty guardrails from PR #10

This gives the repo a much stronger story:
- rule-based MVP baseline
- external benchmark pipelines
- project-native learned baseline (clearly labeled as data-limited if necessary)

## Recommended future architecture
### Keep in repo
- dual external pipeline infrastructure
- comparison report contract
- benchmark artifacts

### Do not wire into runtime yet
- external-trained logistic model in API scoring path

### Add next
- a transfer-check report comparing:
  - rule-based scorer
  - project-native logistic baseline
  - external benchmark observations

## Recommended license stance
For project code, prefer **Apache-2.0**.

Reason:
- permissive
- portfolio-friendly
- clearer patent grant than MIT

Important caveat:
- external datasets are **not automatically covered** by the project code license
- dataset provenance and licensing should be documented separately
- avoid committing raw external data to the repo unless clearly allowed

## Final recommendation
### Adopt now
- Apache-2.0 for code
- IBM as conservative benchmark reference
- Skywalker as high-signal benchmark / stress test
- keep rule-based scorer as main app scorer

### Do next
- build a project-native logistic baseline
- compare it honestly against the rule-based scorer
- only then decide whether the runtime scoring path should change
