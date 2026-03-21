from datetime import date
from decimal import Decimal

from app.ingestion.normalize import (
    normalize_field,
    normalize_row,
)


def test_normalize_amount_accepts_currency_symbols() -> None:
    result = normalize_field(
        canonical_field="total_amount",
        source_field="amount",
        raw_value="$12,345.67",
    )
    assert result.canonical == Decimal("12345.67")
    assert result.canonical_type == "decimal"
    assert result.parse_warning is None


def test_normalize_amount_handles_parentheses_negative() -> None:
    result = normalize_field(
        canonical_field="outstanding_amount",
        source_field="balance",
        raw_value="(1,234.56)",
    )
    assert result.canonical == Decimal("-1234.56")


def test_normalize_amount_returns_warning_on_invalid() -> None:
    result = normalize_field(
        canonical_field="total_amount",
        source_field="amount",
        raw_value="twelve thousand",
    )
    assert result.canonical is None
    assert result.parse_warning is not None


def test_normalize_date_accepts_iso_format() -> None:
    result = normalize_field(
        canonical_field="invoice_date",
        source_field="date",
        raw_value="2026-03-21",
    )
    assert result.canonical == date(2026, 3, 21)
    assert result.canonical_type == "date"


def test_normalize_date_accepts_us_format() -> None:
    result = normalize_field(
        canonical_field="due_date",
        source_field="due",
        raw_value="03/21/2026",
    )
    assert result.canonical == date(2026, 3, 21)


def test_normalize_status_normalizes_variants() -> None:
    for raw, expected in [
        ("Open", "open"),
        ("UNPAID", "open"),
        ("Partially Paid", "partially_paid"),
        ("Paid", "paid"),
        ("Void", "void"),
        ("Written Off", "written_off"),
    ]:
        result = normalize_field(
            canonical_field="status",
            source_field="status",
            raw_value=raw,
        )
        assert result.canonical == expected


def test_normalize_status_returns_warning_on_unknown() -> None:
    result = normalize_field(
        canonical_field="status",
        source_field="status",
        raw_value="pending review",
    )
    assert result.canonical is None
    assert result.parse_warning is not None


def test_normalize_row_returns_warnings_for_missing() -> None:
    result = normalize_row(
        mapped_fields={"external_invoice_id": "invoice_id", "due_date": "due_date"},
        row={"invoice_id": "", "due_date": "2026-03-21"},
    )
    assert "external_invoice_id" in result.values
    assert result.values["external_invoice_id"].canonical is None
    assert any(warning[0] == "external_invoice_id" for warning in result.warnings)


def test_normalize_row_detects_date_parse_issue() -> None:
    result = normalize_row(
        mapped_fields={"due_date": "due_date"},
        row={"due_date": "not-a-date"},
    )
    assert "due_date" in result.values
    assert result.values["due_date"].parse_warning is not None
    assert any(issue[0] == "due_date" for issue in result.issues)