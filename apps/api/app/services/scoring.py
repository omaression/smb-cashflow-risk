from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
import csv

from app.services.features import InvoiceFeatureRow, build_invoice_feature_rows


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
    accuracy: float
    precision: float
    recall: float
    top_features_used: list[str]


def score_feature_row(row: InvoiceFeatureRow) -> BaselineScoreRow:
    raw_score = (
        0.30
        + min(row.overdue_days, 60) * 0.012
        + (0.07 if row.payment_terms_days >= 45 else 0.0)
        + (0.08 if float(row.amount) >= 10000 else 0.0)
        + (0.10 if row.paid_ratio == 0 else 0.04)
        + row.customer_late_invoice_ratio * 0.12
    )
    score = round(max(0.05, min(0.95, raw_score)), 2)

    reasons: list[str] = []
    if row.overdue_days > 0:
        reasons.append("invoice_overdue_days")
    if row.payment_terms_days >= 45:
        reasons.append("extended_payment_terms")
    if float(row.amount) >= 10000:
        reasons.append("customer_concentration_risk")
    if row.paid_ratio == 0:
        reasons.append("no_partial_payments_recorded")
    if row.customer_late_invoice_ratio > 0:
        reasons.append("customer_historical_late_ratio")

    if score >= 0.75:
        bucket = "high"
    elif score >= 0.50:
        bucket = "medium"
    else:
        bucket = "low"

    predicted_label = int(score >= 0.50)
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
    scored_rows = [score_feature_row(row) for row in rows]
    true_positive = sum(1 for row in scored_rows if row.predicted_label == 1 and row.actual_label == 1)
    false_positive = sum(1 for row in scored_rows if row.predicted_label == 1 and row.actual_label == 0)
    false_negative = sum(1 for row in scored_rows if row.predicted_label == 0 and row.actual_label == 1)
    correct = sum(1 for row in scored_rows if row.predicted_label == row.actual_label)

    row_count = len(scored_rows)
    positive_labels = sum(row.actual_label for row in scored_rows)
    predicted_positive = sum(row.predicted_label for row in scored_rows)
    precision = round(true_positive / predicted_positive, 2) if predicted_positive else 0.0
    recall = round(true_positive / positive_labels, 2) if positive_labels else 0.0
    accuracy = round(correct / row_count, 2) if row_count else 0.0

    evaluation = BaselineEvaluation(
        row_count=row_count,
        positive_labels=positive_labels,
        predicted_positive=predicted_positive,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        top_features_used=[
            "overdue_days",
            "payment_terms_days",
            "amount",
            "paid_ratio",
            "customer_late_invoice_ratio",
        ],
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
