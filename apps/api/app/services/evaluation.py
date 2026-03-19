from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import json

from app.services.features import InvoiceFeatureRow
from app.services.model_version import ModelVersion
from app.services.scoring import BaselineScoreRow, score_feature_row

DEFAULT_SPLIT_RATIOS = (0.6, 0.2, 0.2)
MIN_SAMPLES_FOR_MEANINGFUL_METRICS = 10
ARTIFACT_STATUS_DEMONSTRATION_ONLY = "demonstration_only"
ARTIFACT_STATUS_VALID = "computed"


@dataclass(frozen=True)
class DataSplit:
    train: list[InvoiceFeatureRow]
    validation: list[InvoiceFeatureRow]
    test: list[InvoiceFeatureRow]
    is_small_dataset: bool
    warning: str | None = None


@dataclass(frozen=True)
class EvaluationResult:
    split_name: str
    row_count: int
    positive_labels: int
    predicted_positive: int
    accuracy: float | None
    precision: float | None
    recall: float | None
    f1: float | None
    specificity: float | None
    confusion_matrix: dict[str, int]
    metrics_status: str
    warning: str | None
    evaluated_at: str


def split_features(
    rows: list[InvoiceFeatureRow],
    ratios: tuple[float, float, float] = DEFAULT_SPLIT_RATIOS,
) -> DataSplit:
    row_count = len(rows)
    if row_count < MIN_SAMPLES_FOR_MEANINGFUL_METRICS:
        return DataSplit(
            train=list(rows),
            validation=list(rows),
            test=list(rows),
            is_small_dataset=True,
            warning=(
                f"Only {row_count} rows available; returning identical train/validation/test splits for "
                "workflow demonstration only."
            ),
        )

    train_cutoff = ratios[0]
    validation_cutoff = ratios[0] + ratios[1]
    train: list[InvoiceFeatureRow] = []
    validation: list[InvoiceFeatureRow] = []
    test: list[InvoiceFeatureRow] = []

    for row in rows:
        bucket_value = int(sha256(row.invoice_id.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
        if bucket_value < train_cutoff:
            train.append(row)
        elif bucket_value < validation_cutoff:
            validation.append(row)
        else:
            test.append(row)

    return DataSplit(train=train, validation=validation, test=test, is_small_dataset=False)


def _safe_divide(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 2)


def evaluate_model(
    scored_rows: list[BaselineScoreRow],
    split_name: str,
    min_samples_for_metrics: int = MIN_SAMPLES_FOR_MEANINGFUL_METRICS,
) -> EvaluationResult:
    true_positive = sum(1 for row in scored_rows if row.predicted_label == 1 and row.actual_label == 1)
    false_positive = sum(1 for row in scored_rows if row.predicted_label == 1 and row.actual_label == 0)
    true_negative = sum(1 for row in scored_rows if row.predicted_label == 0 and row.actual_label == 0)
    false_negative = sum(1 for row in scored_rows if row.predicted_label == 0 and row.actual_label == 1)

    row_count = len(scored_rows)
    positive_labels = sum(row.actual_label for row in scored_rows)
    negative_labels = row_count - positive_labels
    predicted_positive = sum(row.predicted_label for row in scored_rows)
    now = datetime.now(UTC).isoformat()

    if row_count < min_samples_for_metrics:
        return EvaluationResult(
            split_name=split_name,
            row_count=row_count,
            positive_labels=positive_labels,
            predicted_positive=predicted_positive,
            accuracy=None,
            precision=None,
            recall=None,
            f1=None,
            specificity=None,
            confusion_matrix={"tp": true_positive, "fp": false_positive, "tn": true_negative, "fn": false_negative},
            metrics_status=ARTIFACT_STATUS_DEMONSTRATION_ONLY,
            warning=(
                f"Metrics not computed for split '{split_name}': {row_count} rows is below the minimum "
                f"threshold of {min_samples_for_metrics}."
            ),
            evaluated_at=now,
        )

    accuracy = _safe_divide(true_positive + true_negative, row_count)
    precision = _safe_divide(true_positive, predicted_positive)
    recall = _safe_divide(true_positive, positive_labels)
    specificity = _safe_divide(true_negative, negative_labels)
    f1 = None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = round(2 * precision * recall / (precision + recall), 2)

    return EvaluationResult(
        split_name=split_name,
        row_count=row_count,
        positive_labels=positive_labels,
        predicted_positive=predicted_positive,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        specificity=specificity,
        confusion_matrix={"tp": true_positive, "fp": false_positive, "tn": true_negative, "fn": false_negative},
        metrics_status=ARTIFACT_STATUS_VALID,
        warning=None,
        evaluated_at=now,
    )


def score_and_evaluate_split(rows: list[InvoiceFeatureRow], split_name: str) -> tuple[list[BaselineScoreRow], EvaluationResult]:
    scored_rows = [score_feature_row(row) for row in rows]
    return scored_rows, evaluate_model(scored_rows, split_name)


def _artifact_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def _artifact_suffix(model_version: ModelVersion) -> str:
    return model_version.evaluation_status


def save_evaluation_artifact(
    output_dir: str | Path,
    model_version: ModelVersion,
    split_results: dict[str, EvaluationResult],
    *,
    small_dataset_warning: str | None,
    limitations: list[str],
) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _artifact_timestamp()
    target_path = target_dir / f"{model_version.version}_{timestamp}_WORKFLOW_DEMO.json"

    payload = {
        "model_version": model_version.version,
        "model_type": model_version.model_type,
        "target": model_version.target,
        "decision_threshold": model_version.decision_threshold,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "evaluation_status": model_version.evaluation_status,
        "scoring_parameters": model_version.scoring_parameters,
        "features_used": model_version.features_used,
        "splits": {name: asdict(result) for name, result in split_results.items()},
        "small_dataset_warning": small_dataset_warning,
        "limitations": limitations,
        "notes": model_version.notes,
    }
    target_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target_path


def generate_evaluation_report(
    output_dir: str | Path,
    model_version: ModelVersion,
    split_results: dict[str, EvaluationResult],
    *,
    small_dataset_warning: str | None,
    limitations: list[str],
) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _artifact_timestamp()
    target_path = target_dir / f"{model_version.version}_{timestamp}_{_artifact_suffix(model_version)}_report.md"

    metrics_lines = []
    for name, result in split_results.items():
        metrics_lines.append(
            f"| {name} | {result.row_count} | {result.accuracy} | {result.precision} | {result.recall} | {result.f1} | {result.specificity} |"
        )

    confusion_lines = []
    for name, result in split_results.items():
        cm = result.confusion_matrix
        confusion_lines.append(f"- **{name}**: TP={cm['tp']}, FP={cm['fp']}, TN={cm['tn']}, FN={cm['fn']}")

    limitation_lines = "\n".join(f"- {item}" for item in limitations)
    warning_block = small_dataset_warning or "No small-dataset warning triggered."
    content = f"# Baseline Model Evaluation Report\n\n## ⚠️ Limitations First\n{warning_block}\n\n{limitation_lines}\n\n## Model Identity\n- Version: `{model_version.version}`\n- Type: `{model_version.model_type}`\n- Target: `{model_version.target}`\n- Threshold: `{model_version.decision_threshold}`\n\n## Target Definition\n- `is_late_15` means the invoice was paid 15 or more days after its due date, or remains 15+ days overdue as of the evaluation date.\n- This is an MVP-friendly risk target for receivables prioritization, not a validated production label.\n\n## Scoring Formula\nThe current model is rule-based and uses heuristic weights stored in `model_version.py`. Scores are not calibrated probabilities.\n\n## Metrics\n| Split | Rows | Accuracy | Precision | Recall | F1 | Specificity |\n|---|---:|---:|---:|---:|---:|---:|\n{chr(10).join(metrics_lines)}\n\n## Confusion Matrix\n{chr(10).join(confusion_lines)}\n\n## Next Steps\n- Add more real historical invoice/payment data before claiming predictive performance.\n- Compare this baseline against a simple learned model only after enough labeled samples exist.\n- Keep the artifact/report path stable so future model versions remain comparable.\n"
    target_path.write_text(content, encoding="utf-8")
    return target_path
