from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass(frozen=True)
class NormalizedValue:
    raw: str | None
    canonical: Any
    canonical_type: str
    parse_warning: str | None


@dataclass(frozen=True)
class NormalizeResult:
    values: dict[str, NormalizedValue]
    issues: list[tuple[str, str, str]]
    warnings: list[tuple[str, str, str]]


_DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d-%b-%Y",
    "%d %B %Y",
    "%B %d, %Y",
    "%b %d, %Y",
]


def _normalize_amount_decimal(raw: str) -> tuple[Decimal | None, str | None]:
    if not raw:
        return None, "empty amount"
    text = raw.strip()
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    for sym in ("$", "€", "£", "₹", "¥", "USD", "EUR", "GBP"):
        text = text.replace(sym, "")
    text = text.replace(",", "").strip()
    try:
        value = Decimal(text)
        return value, None
    except (InvalidOperation, ValueError):
        return None, f"unparseable amount: {raw}"


def _normalize_date(raw: str) -> tuple[date | None, str | None]:
    if not raw:
        return None, "empty date"
    text = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date(), None
        except ValueError:
            continue
    # Fallback: try generic ISO-like parse
    iso_match = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$", text)
    if iso_match:
        try:
            return date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))), None
        except ValueError:
            return None, f"invalid date: {raw}"
    return None, f"unparseable date: {raw}"


_STATUS_MAP = {
    "open": "open",
    "unpaid": "open",
    "outstanding": "open",
    "pending": "open",
    "partial": "partially_paid",
    "partially paid": "partially_paid",
    "partially_paid": "partially_paid",
    "paid": "paid",
    "closed": "paid",
    "settled": "paid",
    "void": "void",
    "cancelled": "void",
    "canceled": "void",
    "written_off": "written_off",
    "write_off": "written_off",
}


def _normalize_status(raw: str) -> tuple[str | None, str | None]:
    if not raw:
        return None, "empty status"
    key = raw.strip().lower().replace("-", "_").replace(" ", "_")
    canonical = _STATUS_MAP.get(key)
    if canonical:
        return canonical, None
    # Allow exact matches
    if key in {"open", "partially_paid", "paid", "void", "written_off"}:
        return key, None
    return None, f"unrecognized status: {raw}"


_BOOL_TRUE = {"true", "1", "yes", "y", "on"}
_BOOL_FALSE = {"false", "0", "no", "n", "off"}


def _normalize_bool(raw: str) -> tuple[bool | None, str | None]:
    if not raw:
        return None, "empty boolean"
    key = raw.strip().lower()
    if key in _BOOL_TRUE:
        return True, None
    if key in _BOOL_FALSE:
        return False, None
    return None, f"unparseable boolean: {raw}"


def normalize_field(
    *,
    canonical_field: str,
    source_field: str,
    raw_value: str | None,
) -> NormalizedValue:
    if raw_value is None or raw_value == "":
        return NormalizedValue(raw=None, canonical=None, canonical_type="null", parse_warning="missing")

    parsers = {
        "invoice_date": lambda v: _normalize_date(v),
        "due_date": lambda v: _normalize_date(v),
        "payment_date": lambda v: _normalize_date(v),
        "snapshot_date": lambda v: _normalize_date(v),
        "total_amount": lambda v: _normalize_amount_decimal(v),
        "subtotal_amount": lambda v: _normalize_amount_decimal(v),
        "outstanding_amount": lambda v: _normalize_amount_decimal(v),
        "amount": lambda v: _normalize_amount_decimal(v),
        "paid_amount": lambda v: _normalize_amount_decimal(v),
        "opening_balance": lambda v: _normalize_amount_decimal(v),
        "cash_in": lambda v: _normalize_amount_decimal(v),
        "cash_out": lambda v: _normalize_amount_decimal(v),
        "closing_balance": lambda v: _normalize_amount_decimal(v),
        "status": lambda v: _normalize_status(v),
        "payment_terms_days": lambda v: (
            (int(float(v.strip())), None)
            if v.strip() and re.match(r"^-?\d+(\.\d+)?$", v.strip())
            else (None, f"unparseable integer: {v}")
        ),
        "credit_limit": lambda v: _normalize_amount_decimal(v),
        "is_active": lambda v: _normalize_bool(v),
    }

    parser = parsers.get(canonical_field)
    if parser is None:
        return NormalizedValue(raw=raw_value, canonical=raw_value, canonical_type="string", parse_warning=None)

    value, warning = parser(raw_value)
    if value is None:
        return NormalizedValue(raw=raw_value, canonical=None, canonical_type="null", parse_warning=warning)

    type_name = {
        "invoice_date": "date",
        "due_date": "date",
        "payment_date": "date",
        "snapshot_date": "date",
        "total_amount": "decimal",
        "subtotal_amount": "decimal",
        "outstanding_amount": "decimal",
        "amount": "decimal",
        "paid_amount": "decimal",
        "opening_balance": "decimal",
        "cash_in": "decimal",
        "cash_out": "decimal",
        "closing_balance": "decimal",
        "status": "status",
        "payment_terms_days": "integer",
        "credit_limit": "decimal",
        "is_active": "boolean",
    }.get(canonical_field, "unknown")

    return NormalizedValue(raw=raw_value, canonical=value, canonical_type=type_name, parse_warning=None)


def normalize_row(
    *,
    mapped_fields: dict[str, str],
    row: dict[str, str],
) -> NormalizeResult:
    values: dict[str, NormalizedValue] = {}
    issues: list[tuple[str, str, str]] = []
    warnings: list[tuple[str, str, str]] = []

    for canonical_field, source_field in mapped_fields.items():
        raw = row.get(source_field)
        normalized = normalize_field(canonical_field=canonical_field, source_field=source_field, raw_value=raw)
        values[canonical_field] = normalized
        if normalized.parse_warning:
            if normalized.canonical is None and raw not in (None, ""):
                issues.append((canonical_field, source_field, normalized.parse_warning))
            elif normalized.canonical is None:
                warnings.append((canonical_field, source_field, normalized.parse_warning))

    return NormalizeResult(values=values, issues=issues, warnings=warnings)