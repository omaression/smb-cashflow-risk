from app.ingestion.validation import (
    IssueCategory,
    IssueSeverity,
    compute_dataset_validation_summary,
    validate_amount_consistency,
    validate_duplicate_ids,
    validate_row_presence,
    validate_status_consistency,
    validate_temporal_consistency,
)
from datetime import date
from decimal import Decimal


def test_validate_row_presence_flags_missing() -> None:
    issues = validate_row_presence(
        canonical_field="external_invoice_id",
        raw_value=None,
        row_number=2,
    )
    assert len(issues) == 1
    assert issues[0].severity == IssueSeverity.HIGH
    assert issues[0].category == IssueCategory.MISSINGNESS


def test_validate_row_presence_accepts_present() -> None:
    issues = validate_row_presence(
        canonical_field="external_invoice_id",
        raw_value="INV-123",
        row_number=2,
    )
    assert len(issues) == 0


def test_validate_temporal_consistency_flags_due_before_invoice() -> None:
    issues = validate_temporal_consistency(
        earlier_field="invoice_date",
        earlier_value=date(2026, 3, 21),
        later_field="due_date",
        later_value=date(2026, 3, 15),
        row_number=3,
    )
    assert len(issues) == 1
    assert issues[0].severity == IssueSeverity.HIGH
    assert issues[0].category == IssueCategory.TEMPORAL_INCONSISTENCY


def test_validate_temporal_consistency_accepts_valid_dates() -> None:
    issues = validate_temporal_consistency(
        earlier_field="invoice_date",
        earlier_value=date(2026, 3, 15),
        later_field="due_date",
        later_value=date(2026, 3, 21),
        row_number=3,
    )
    assert len(issues) == 0


def test_validate_amount_consistency_flags_outstanding_exceeds_total() -> None:
    issues = validate_amount_consistency(
        total_field="total_amount",
        total_value=Decimal("1000.00"),
        outstanding_field="outstanding_amount",
        outstanding_value=Decimal("1200.00"),
        row_number=5,
    )
    assert len(issues) == 1
    assert issues[0].severity == IssueSeverity.HIGH
    assert issues[0].category == IssueCategory.AMOUNT_INCONSISTENCY


def test_validate_amount_consistency_accepts_partial_payment() -> None:
    issues = validate_amount_consistency(
        total_field="total_amount",
        total_value=Decimal("1000.00"),
        outstanding_field="outstanding_amount",
        outstanding_value=Decimal("400.00"),
        row_number=5,
    )
    assert len(issues) == 0


def test_validate_status_consistency_flags_paid_with_outstanding() -> None:
    issues = validate_status_consistency(
        status_field="status",
        status_value="paid",
        outstanding_value=Decimal("150.00"),
        row_number=6,
    )
    assert len(issues) == 1
    assert issues[0].severity == IssueSeverity.MEDIUM
    assert issues[0].category == IssueCategory.STATUS_INCONSISTENCY


def test_validate_status_consistency_flags_open_with_zero_outstanding() -> None:
    issues = validate_status_consistency(
        status_field="status",
        status_value="open",
        outstanding_value=Decimal("0"),
        row_number=6,
    )
    assert len(issues) == 1


def test_validate_duplicate_ids_flags_duplicates() -> None:
    ids = [(1, "INV-1"), (2, "INV-2"), (3, "INV-1")]
    issues = validate_duplicate_ids(id_field="external_invoice_id", id_values=ids)
    assert len(issues) == 1
    assert issues[0].row_number == 3
    assert "Duplicate" in issues[0].message


def test_compute_dataset_validation_summary_counts_severities() -> None:
    issues = [
        validate_row_presence(canonical_field="field_a", raw_value=None, row_number=1)[0],
        validate_temporal_consistency(
            earlier_field="invoice_date",
            earlier_value=date(2026, 3, 21),
            later_field="due_date",
            later_value=date(2026, 3, 15),
            row_number=2,
        )[0],
    ]
    summary = compute_dataset_validation_summary(total_rows=5, issues=issues)
    assert summary.total_rows == 5
    assert summary.high_count == 2
    assert summary.fatal_count == 0