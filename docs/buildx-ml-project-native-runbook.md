# Buildx Runbook — Project-Native ML Pipeline Readiness

Branch: `feat/ml-project-native-logistic-baseline`

## Goal
Build a project-native ML pipeline path that can honestly defer learned-model claims until enough native data exists, while proving the adapter/pipeline/artifact path is ready.

## Step status
1. parallel-plan-a — DONE (`uploads/ml-project-native-plan-codex.md`)
2. parallel-plan-b — DONE (`uploads/ml-project-native-plan-glm5.md`)
3. judge-plan — DONE
4. boilerplate — DONE
5. implement — DONE
6. test — DONE
7. simplify — DONE
8. retest — DONE
9. review-resolve-a — DONE
10. test-a — IN PROGRESS
11. review-resolve-b — DONE
12. final-test — PENDING

## Judge-plan synthesis
### Selected architecture
- native adapter under `app.ml.adapters`
- native pipeline entrypoint under `app.ml.pipelines`
- workflow-demo reporting for too-small native data
- CI hook to run native readiness script

### Why it won
- keeps runtime scorer unchanged
- proves the native ML path exists
- avoids fake metrics on 3 invoices
- aligns with PR #10 honesty constraints and PR #11 external benchmark structure

### Scope boundary
In scope:
- native adapter
- native pipeline wiring
- native workflow-demo artifact generation
- docs/tests/CI

Out of scope:
- meaningful native model training claims
- runtime scorer replacement
- learned-vs-rule predictive comparison on tiny native data
