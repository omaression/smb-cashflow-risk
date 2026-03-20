# ML External Data Plan

## Goal
Use external invoice-payment datasets as **benchmark evidence** and feature-discovery sources without overclaiming transferability into the runtime app.

## Public framing
This project uses two external dataset families to explore whether learned baselines can capture useful signal in invoice-payment behavior.

The purpose is to:
- test benchmark pipelines
- compare modeling behavior across distinct data sources
- identify ideas worth considering for future project-native ML work

The purpose is **not** to claim that external benchmark performance automatically transfers into `smb-cashflow-risk` runtime scoring.

## Dataset policy
- keep datasets separate
- document provenance and caveats
- exclude post-outcome information from training features
- prefer temporal validation where possible
- reject any dataset that looks strong only because of leakage or weak provenance

## Deliverables
- dataset-specific normalized snapshots
- dataset-specific logistic baseline artifacts
- side-by-side comparison report
- public recommendation on what should and should not transfer into the app
