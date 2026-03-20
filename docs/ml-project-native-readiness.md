# Project-Native ML Readiness

## Current decision
The repository now has a **project-native ML pipeline path**, but it is currently restricted to **workflow-demo mode**.

## Why training is deferred
The current project-native sample data is too small for meaningful learned-model training:
- only a handful of invoices
- too few positive `is_late_15` examples
- no honest basis for train/validation/test model claims

## What the current phase proves
- the native adapter works
- the native pipeline wiring works
- the project can emit native ML artifacts/reports
- deferral logic works when sample size is too small

## What it does not prove
- that a native logistic baseline is currently meaningful
- that a learned model beats the rule-based scorer
- that runtime scoring should change now

## Future unlock condition
To move beyond workflow-demo mode, the project should have roughly:
- 100+ rows before even considering holdout training
- 500+ rows for more credible metrics
- enough positive late-payment examples to avoid degenerate evaluation
- leakage-safe snapshot-aware features rather than simple end-state export rows
