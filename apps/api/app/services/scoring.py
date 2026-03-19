from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
import csv

from app.services.features import InvoiceFeatureRow, build_invoice_feature_rows
from app.services.model_version import CURRENT_MODEL_VERSION, SCORING_PARAMETERS


@dataclass(frozen=True)
class BaselineScoreRow:
    invoice_id: str
    customer_id: str
    score: float
    predicted_label: int
    actual_label: int
    risk_bucket: str
    top_reason_codes: list[str]


@dataclass(frozen=True)
class BaselineEvaluation:
    row_count: int
    positive_labels: int
    predicted_positive: int
    accuracy: float | None
    precision: float | None
    recall: float | None
    top_features_used: list[str]
    metrics_status: str = "computed"
    warning: str | None = None


def score_feature_row(row: InvoiceFeatureRow) -> BaselineScoreRow:
    raw_score = (
        SCORING_PARAMETERS["base_score"]
        + min(row.overdue_days, SCORING_PARAMETERS["max_overdue_days"]) * SCORING_PARAMETERS["overdue_days_weight"]
        + (
            SCORING_PARAMETERS["extended_terms_penalty"]
            if row.payment_terms_days >= SCORING_PARAMETERS["extended_terms_threshold"]
            else 0.0
        )
        + (
            SCORING_PARAMETERS["large_invoice_penalty"]
            if float(row.amount) >= SCORING_PARAMETERS["large_invoice_threshold"]
            else 0.0
        )
        + (
            SCORING_PARAMETERS["no_partial_payments_penalty"]
            if row.paid_ratio == 0
            else SCORING_PARAMETERS["partial_payments_penalty"]
        )
        + row.customer_late_invoice_ratio * SCORING_PARAMETERS["customer_late_ratio_weight"]
    )
    score = round(max(SCORING_PARAMETERS["min_score"], min(SCORING_PARAMETERS["max_score"], raw_score)), 2)

    reasons: list[str] = []
    if row.overdue_days > 0:
        reasons.append("invoice_overdue_days")
    if row.payment_terms_days >= SCORING_PARAMETERS["extended_terms_threshold"]:
        reasons.append("extended_payment_terms")
    if float(row.amount) >= SCORING_PARAMETERS["large_invoice_threshold"]:
        reasons.append("customer_concentration_risk")
    if row.paid_ratio == 0:
        reasons.append("no_partial_payments_recorded")
    if row.customer_late_invoice_ratio > 0:
        reasons.append("customer_historical_late_ratio")

    if score >= SCORING_PARAMETERS["high_risk_threshold"]:
        bucket = "high"
    elif score >= SCORING_PARAMETERS["medium_risk_threshold"]:
        bucket = "medium"
    else:
        bucket = "low"

    predicted_label = int(score >= CURRENT_MODEL_VERSION.decision_threshold)
    return BaselineScoreRow(
        invoice_id=row.invoice_id,
        customer_id=row.customer_id,
        score=score,
        predicted_label=predicted_label,
        actual_label=row.is_late_15,
        risk_bucket=bucket,
        top_reason_codes=reasons[:3],
    )


def evaluate_baseline(rows: list[InvoiceFeatureRow]) -> tuple[list[BaselineScoreRow], BaselineEvaluation]:
    from app.services.evaluation import evaluate_model

    scored_rows = [score_feature_row(row) for row in rows]
    evaluation_result = evaluate_model(scored_rows, "all_rows")
    evaluation = BaselineEvaluation(
        row_count=evaluation_result.row_count,
        positive_labels=evaluation_result.positive_labels,
        predicted_positive=evaluation_result.predicted_positive,
        accuracy=evaluation_result.accuracy,
        precision=evaluation_result.precision,
        recall=evaluation_result.recall,
        top_features_used=CURRENT_MODEL_VERSION.features_used,
        metrics_status=evaluation_result.metrics_status,
        warning=evaluation_result.warning,
    )
    return scored_rows, evaluation


def export_feature_rows_to_csv(rows: list[InvoiceFeatureRow], path: str | Path) -> Path:
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [field.name for field in fields(InvoiceFeatureRow)]
    with target_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    return target_path


def build_and_export_features(session, path: str | Path) -> Path:
    rows = build_invoice_feature_rows(session)
    if not rows:
        raise ValueError("no invoice features available to export")
    return export_feature_rows_to_csv(rows, path)
