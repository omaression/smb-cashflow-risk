# Buildx Runbook — Dual-Dataset ML Phase A

Branch: `feat/ml-external-data-and-baselines`

## Goal
Build two honest, separate learned-model pipelines on distinct invoice-payment datasets, compare them through a shared evaluation/report contract, and decide what should or should not transfer into `smb-cashflow-risk`.

## Step status
1. parallel-plan-a — DONE (`uploads/ml-dual-dataset-plan-codex.md`)
2. parallel-plan-b — DONE (`uploads/ml-dual-dataset-plan-glm5.md`)
3. judge-plan — DONE
4. boilerplate — DONE
5. implement — DONE
6. test — DONE
7. simplify — DONE
8. retest — DONE
9. review-resolve-a — PENDING
10. test-a — PENDING
11. review-resolve-b — PENDING
12. final-test — PENDING

## Judge-plan synthesis
### Selected architecture
- shared dataset registry + normalization/evaluation spine
- separate dataset adapters for IBM/Kaggle and Skywalker
- separate logistic-regression baselines
- shared comparison report
- no row-wise dataset merge in Phase A

### Why it won
- keeps provenance clear
- prevents silent cross-dataset leakage
- preserves honest comparison
- maps cleanly onto the credibility layer merged in PR #10

### Scope boundary
In scope:
- dataset registry/config
- two dataset adapters
- leakage exclusion config
- target construction
- logistic baseline training/evaluation
- side-by-side comparison artifact/report

Out of scope:
- merging the two datasets
- replacing production scoring in the app
- XGBoost/trees before logistic baseline is understood
- claims of production transferability

### Main risks
- leakage through post-outcome columns
- target mismatch between datasets
- overclaiming transferability to `smb-cashflow-risk`
- noisy one-off scripts instead of stable project structure
