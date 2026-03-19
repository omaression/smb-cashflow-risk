# ML External Data Plan

## Phase A goal
Run two separate learned-model pipelines on distinct invoice-payment datasets and compare them honestly through a shared evaluation/report contract.

## Datasets
### IBM/Kaggle local upload
- Source file: `../uploads/20260319_091134_AgADHAcAArMx4EU.csv`
- Approx shape: 2,466 rows x 12 columns
- Main risk: direct leakage from `DaysToSettle`, `SettledDate`, `PaperlessDate`
- Main target: `is_late_15`

### Skywalker raw GitHub dataset
- Source URL: `https://raw.githubusercontent.com/SkywalkerHub/Payment-Date-Prediction/main/Dataset.csv`
- Approx shape after normalization: 45k+ rows
- Main risk: leakage from `clear_date` and open/settlement-adjacent fields
- Main target: `is_late_15`

## Decision policy
- Do not merge datasets row-wise in Phase A.
- Do not replace production scoring based on external-data metrics alone.
- Prefer temporal splits over random splits.
- If a dataset only wins because of likely leakage, reject it.

## Deliverables
- dataset-specific normalized snapshots
- dataset-specific logistic baseline artifacts
- side-by-side comparison report
- recommendation on what should transfer into `smb-cashflow-risk`
