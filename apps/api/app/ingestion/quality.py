from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class QualityDimension:
    name: str
    score: float
    weight: float
    issues: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QualityProfile:
    completeness: QualityDimension
    consistency: QualityDimension
    coverage: QualityDimension
    history_depth: QualityDimension
    sample_size: QualityDimension
    overall_score: float
    reliability_grade: str
    recommendations: list[str]


def compute_completeness(
    *,
    required_fields: list[str],
    present_fields: list[str],
    row_count: int,
    missing_field_ratio: float,
) -> QualityDimension:
    score = max(0.0, 1.0 - missing_field_ratio * 1.5)
    issues: list[str] = []

    missing = [f for f in required_fields if f not in present_fields]
    if missing:
        issues.append(f"Missing required fields: {', '.join(missing[:3])}")
    if row_count == 0:
        issues.append("Empty dataset")
        score = 0.0

    return QualityDimension(
        name="completeness",
        score=min(1.0, max(0.0, score)),
        weight=0.25,
        issues=issues,
    )


def compute_consistency(
    *,
    duplicate_id_count: int,
    ambiguous_mapping_count: int,
    temporal_violation_count: int,
    amount_violation_count: int,
    status_violation_count: int,
    row_count: int,
) -> QualityDimension:
    if row_count == 0:
        return QualityDimension(
            name="consistency",
            score=0.0,
            weight=0.20,
            issues=["Empty dataset"],
        )

    total_violations = duplicate_id_count + ambiguous_mapping_count + temporal_violation_count + amount_violation_count + status_violation_count
    violation_ratio = total_violations / max(row_count, 1)
    score = max(0.0, 1.0 - violation_ratio * 2.0)

    issues: list[str] = []
    if duplicate_id_count > 0:
        issues.append(f"{duplicate_id_count} duplicate IDs")
    if ambiguous_mapping_count > 0:
        issues.append(f"{ambiguous_mapping_count} ambiguous mappings")
    if temporal_violation_count > 0:
        issues.append(f"{temporal_violation_count} temporal inconsistencies")
    if amount_violation_count > 0:
        issues.append(f"{amount_violation_count} amount inconsistencies")
    if status_violation_count > 0:
        issues.append(f"{status_violation_count} status inconsistencies")

    return QualityDimension(
        name="consistency",
        score=min(1.0, max(0.0, score)),
        weight=0.20,
        issues=issues,
    )


def compute_coverage(
    *,
    observed_customers: int,
    observed_invoices: int,
    observed_payments: int,
    expected_customer_count: int | None,
    expected_invoice_count: int | None,
) -> QualityDimension:
    issues: list[str] = []

    if expected_customer_count and observed_customers < expected_customer_count:
        customer_ratio = observed_customers / expected_customer_count
    elif expected_customer_count:
        customer_ratio = 1.0
    else:
        customer_ratio = 0.8

    if expected_invoice_count and observed_invoices < expected_invoice_count:
        invoice_ratio = observed_invoices / expected_invoice_count
    elif expected_invoice_count:
        invoice_ratio = 1.0
    else:
        invoice_ratio = 0.8

    if observed_customers == 0:
        issues.append("No customers observed")
        customer_ratio = 0.0
    if observed_invoices == 0:
        issues.append("No invoices observed")
        invoice_ratio = 0.0

    payment_bonus = 0.1 if observed_payments > 0 else 0.0
    score = min(1.0, (customer_ratio * 0.5 + invoice_ratio * 0.5 + payment_bonus))

    if observed_payments == 0:
        issues.append("No payment history available")

    return QualityDimension(
        name="coverage",
        score=min(1.0, max(0.0, score)),
        weight=0.20,
        issues=issues,
    )


def compute_history_depth(
    *,
    earliest_date_days_ago: int | None,
    latest_date_days_ago: int | None,
    payment_history_months: int | None,
) -> QualityDimension:
    issues: list[str] = []

    if earliest_date_days_ago is None or latest_date_days_ago is None:
        return QualityDimension(
            name="history_depth",
            score=0.0,
            weight=0.20,
            issues=["No temporal data available"],
        )

    span_days = max(0, earliest_date_days_ago - latest_date_days_ago)
    recent_penalty = max(0, 90 - earliest_date_days_ago) / 90 * 0.5

    if payment_history_months is None or payment_history_months == 0:
        payment_score = 0.2
        issues.append("No payment history depth")
    else:
        payment_score = min(1.0, payment_history_months / 12)

    score = (span_days / 365) * 0.3 + recent_penalty * 0.3 + payment_score * 0.4

    if earliest_date_days_ago > 180:
        issues.append(f"Data starts {earliest_date_days_ago} days ago")

    return QualityDimension(
        name="history_depth",
        score=min(1.0, max(0.0, score)),
        weight=0.20,
        issues=issues,
    )


def compute_sample_size(
    *,
    invoice_count: int,
    customer_count: int,
    min_invoices: int = 50,
    min_customers: int = 5,
) -> QualityDimension:
    issues: list[str] = []

    invoice_score = min(1.0, invoice_count / min_invoices)
    customer_score = min(1.0, customer_count / min_customers)

    score = invoice_score * 0.6 + customer_score * 0.4

    if invoice_count < min_invoices:
        issues.append(f"Only {invoice_count} invoices (recommend {min_invoices})")
    if customer_count < min_customers:
        issues.append(f"Only {customer_count} customers (recommend {min_customers})")

    return QualityDimension(
        name="sample_size",
        score=min(1.0, max(0.0, score)),
        weight=0.15,
        issues=issues,
    )


def compute_overall_quality(
    completeness: QualityDimension,
    consistency: QualityDimension,
    coverage: QualityDimension,
    history_depth: QualityDimension,
    sample_size: QualityDimension,
) -> float:
    weighted_sum = (
        completeness.score * completeness.weight
        + consistency.score * consistency.weight
        + coverage.score * coverage.weight
        + history_depth.score * history_depth.weight
        + sample_size.score * sample_size.weight
    )
    total_weight = (
        completeness.weight
        + consistency.weight
        + coverage.weight
        + history_depth.weight
        + sample_size.weight
    )
    return weighted_sum / total_weight


def reliability_grade(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "moderate"
    if score >= 0.40:
        return "low"
    return "insufficient"


def generate_recommendations(
    *,
    completeness: QualityDimension,
    consistency: QualityDimension,
    coverage: QualityDimension,
    history_depth: QualityDimension,
    sample_size: QualityDimension,
    observed_payments: int,
) -> list[str]:
    recs: list[str] = []

    if completeness.score < 0.7:
        recs.append("Add missing required fields to improve completeness and scoring reliability.")
    if consistency.score < 0.7:
        recs.append("Resolve duplicate IDs, ambiguous column mappings, and temporal/amount inconsistencies.")
    if coverage.score < 0.7:
        recs.append("Extend coverage by including more customers and invoices.")
    if history_depth.score < 0.7:
        recs.append("Provide a longer historical window and payment history for time-based modeling.")
    if sample_size.score < 0.7:
        recs.append("Increase sample size for more stable risk estimates.")
    if observed_payments == 0:
        recs.append("Add payment history to enable payment-behavior features and calibrate forecast confidence.")

    return recs[:5]


def build_quality_profile(
    *,
    required_fields: list[str],
    present_fields: list[str],
    row_count: int,
    missing_field_ratio: float,
    duplicate_id_count: int,
    ambiguous_mapping_count: int,
    temporal_violation_count: int,
    amount_violation_count: int,
    status_violation_count: int,
    observed_customers: int,
    observed_invoices: int,
    observed_payments: int,
    expected_customer_count: int | None = None,
    expected_invoice_count: int | None = None,
    earliest_date_days_ago: int | None = None,
    latest_date_days_ago: int | None = None,
    payment_history_months: int | None = None,
) -> QualityProfile:
    completeness = compute_completeness(
        required_fields=required_fields,
        present_fields=present_fields,
        row_count=row_count,
        missing_field_ratio=missing_field_ratio,
    )

    consistency = compute_consistency(
        duplicate_id_count=duplicate_id_count,
        ambiguous_mapping_count=ambiguous_mapping_count,
        temporal_violation_count=temporal_violation_count,
        amount_violation_count=amount_violation_count,
        status_violation_count=status_violation_count,
        row_count=row_count,
    )

    coverage = compute_coverage(
        observed_customers=observed_customers,
        observed_invoices=observed_invoices,
        observed_payments=observed_payments,
        expected_customer_count=expected_customer_count,
        expected_invoice_count=expected_invoice_count,
    )

    history_depth = compute_history_depth(
        earliest_date_days_ago=earliest_date_days_ago,
        latest_date_days_ago=latest_date_days_ago,
        payment_history_months=payment_history_months,
    )

    sample_size = compute_sample_size(
        invoice_count=observed_invoices,
        customer_count=observed_customers,
    )

    overall = compute_overall_quality(completeness, consistency, coverage, history_depth, sample_size)
    grade = reliability_grade(overall)
    recs = generate_recommendations(
        completeness=completeness,
        consistency=consistency,
        coverage=coverage,
        history_depth=history_depth,
        sample_size=sample_size,
        observed_payments=observed_payments,
    )

    return QualityProfile(
        completeness=completeness,
        consistency=consistency,
        coverage=coverage,
        history_depth=history_depth,
        sample_size=sample_size,
        overall_score=overall,
        reliability_grade=grade,
        recommendations=recs,
    )