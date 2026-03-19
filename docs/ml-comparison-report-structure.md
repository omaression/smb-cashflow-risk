# ML Comparison Report Structure

## Purpose
Compare two external invoice-payment pipelines honestly, without claiming that either one transfers directly into production `smb-cashflow-risk` behavior.

## Required sections
1. Dataset provenance
2. Schema and target definition
3. Leakage exclusions
4. Train/validation/test split policy
5. Model family used
6. Metrics table
7. Tradeoffs and caveats
8. Recommendation for project transferability

## Honesty rules
- Never present external-dataset metrics as production validation for `smb-cashflow-risk`.
- Explicitly state when one dataset appears stronger only because it is larger or cleaner.
- Prefer project-fit and leakage confidence over raw metric wins.
- Reject any winner whose feature set depends on post-outcome information.
