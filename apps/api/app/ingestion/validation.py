from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class IssueSeverity(str, Enum):
    FATAL = "fatal"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(str, Enum):
    MAPPING = "mapping"
    MISSINGNESS = "missingness"
    TYPE_FORMAT = "type_format"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    AMOUNT_INCONSISTENCY = "amount_inconsistency"
    STATUS_INCONSISTENCY = "status_inconsistency"
    DUPLICATE_CONFLICT = "duplicate_conflict"
    STALE_DATA = "stale_data"
    LOW_HISTORY_DEPTH = "low_history_depth"
    LOW_PAYMENT_OBSERVABILITY = "low_payment_observability"
    CUSTOMER_FRAGMENTATION = "customer_fragmentation"


@dataclass(frozen=True)
class ValidationIssue:
    severity: IssueSeverity
    category: IssueCategory
    field: str | None
    row_number: int | None
    message: str
    detail: dict[str, Any] | None = None


@dataclass(frozen=True)
class RowValidationResult:
    row_number: int
    is_valid: bool
    issues: list[ValidationIssue]


@dataclass(frozen=True)
class DatasetValidationResult:
    total_rows: int
    valid_rows: int
    issues: list[ValidationIssue]
    issue_counts: dict[str, int]
    fatal_count: int
    high_count: int
    medium_count: int
    low_count: int


# Severity thresholds for dataset-level extrapolation
_MAX_FATAL_RATIO = 0.0
_MAX_HIGH_RATIO = 0.05
_MAX_MEDIUM_RATIO = 0.20


def validate_row_presence(*, canonical_field: str, raw_value: str | None, row_number: int) -> list[ValidationIssue]:
    if raw_value is None or raw_value == "":
        return [
            ValidationIssue(
                severity=IssueSeverity.HIGH,
                category=IssueCategory.MISSINGNESS,
                field=canonical_field,
                row_number=row_number,
                message=f"Missing required field: {canonical_field}",
            )
        ]
    return []


def validate_temporal_consistency(
    *,
    earlier_field: str,
    earlier_value: Any,
    later_field: str,
    later_value: Any,
    row_number: int,
    detail: dict[str, Any] | None = None,
) -> list[ValidationIssue]:
    from datetime import date

    if isinstance(earlier_value, date) and isinstance(later_value, date):
        if later_value < earlier_value:
            return [
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.TEMPORAL_INCONSISTENCY,
                    field=later_field,
                    row_number=row_number,
                    message=f"{later_field} {later_value} is before {earlier_field} {earlier_value}",
                    detail=detail,
                )
            ]
    return []


def validate_amount_consistency(
    *,
    total_field: str,
    total_value: Any,
    outstanding_field: str,
    outstanding_value: Any,
    row_number: int,
) -> list[ValidationIssue]:
    from decimal import Decimal

    if isinstance(total_value, Decimal) and isinstance(outstanding_value, Decimal):
        if outstanding_value > total_value:
            return [
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.AMOUNT_INCONSISTENCY,
                    field=outstanding_field,
                    row_number=row_number,
                    message=f"{outstanding_field} {outstanding_value} exceeds {total_field} {total_value}",
                )
            ]
    return []


def validate_status_consistency(
    *,
    status_field: str,
    status_value: Any,
    outstanding_value: Any,
    row_number: int,
) -> list[ValidationIssue]:
    from decimal import Decimal

    issues: list[ValidationIssue] = []
    if isinstance(outstanding_value, Decimal):
        if status_value == "paid" and outstanding_value > Decimal("0"):
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.STATUS_INCONSISTENCY,
                    field=status_field,
                    row_number=row_number,
                    message=f"Status is 'paid' but {outstanding_value} remains outstanding",
                )
            )
        if status_value == "open" and outstanding_value == Decimal("0"):
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.STATUS_INCONSISTENCY,
                    field=status_field,
                    row_number=row_number,
                    message="Status is 'open' but outstanding amount is zero",
                )
            )
    return issues


def validate_duplicate_ids(
    *,
    id_field: str,
    id_values: list[tuple[int, str]],
) -> list[ValidationIssue]:
    seen: dict[str, int] = {}
    issues: list[ValidationIssue] = []

    for row_number, value in id_values:
        if value in seen:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.DUPLICATE_CONFLICT,
                    field=id_field,
                    row_number=row_number,
                    message=f"Duplicate {id_field} '{value}' first seen at row {seen[value]}",
                )
            )
        else:
            seen[value] = row_number
    return issues


def compute_dataset_validation_summary(
    *,
    total_rows: int,
    issues: list[ValidationIssue],
) -> DatasetValidationResult:
    fatal_count = sum(1 for issue in issues if issue.severity == IssueSeverity.FATAL)
    high_count = sum(1 for issue in issues if issue.severity == IssueSeverity.HIGH)
    medium_count = sum(1 for issue in issues if issue.severity == IssueSeverity.MEDIUM)
    low_count = sum(1 for issue in issues if issue.severity == IssueSeverity.LOW)

    issue_counts: dict[str, int] = {}
    for issue in issues:
        key = f"{issue.severity.value}:{issue.category.value}"
        issue_counts[key] = issue_counts.get(key, 0) + 1

    return DatasetValidationResult(
        total_rows=total_rows,
        valid_rows=total_rows - len({issue.row_number for issue in issues if issue.row_number is not None}),
        issues=issues,
        issue_counts=issue_counts,
        fatal_count=fatal_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
    )