# ML Transfer Recommendation

## Executive decision
Do **not** replace the current in-app rule-based scorer with an external-data model at this stage.

## Why
The external learned baselines are useful as:
- benchmark evidence
- feature-discovery inputs
- proof that the repo can support learned-model workflows honestly

But they are **not** the same thing as validated production fit for `smb-cashflow-risk`.

## What should transfer now
### Keep the current runtime scorer
The rule-based scorer should remain the default because it is:
- already integrated
- interpretable
- stable for the portfolio MVP
- more honest than promoting an external benchmark model into runtime use prematurely

### Transfer ideas, not model weights
The right things to carry forward are:
- stronger temporal validation discipline
- better threshold-selection practice
- cleaner separation between scoring logic and artifact generation
- feature ideas worth testing later in project-native ML work

## How to interpret the benchmark pipelines
- one external dataset can be used as a conservative benchmark reference
- another can act as a higher-signal stress test
- neither should be treated as direct proof that the runtime app is ML-validated

## Next responsible step
Build on project-native data only when enough native evidence exists to support meaningful training and comparison.
