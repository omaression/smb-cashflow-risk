from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from io import StringIO


@dataclass(frozen=True)
class FileRoleDetection:
    role: str | None
    confidence: float
    alternatives: list[tuple[str, float]]
    reasons: list[str]
    headers: list[str]
    row_count: int


_ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "invoices": (
        "invoice",
        "invoice_id",
        "invoice_number",
        "invoice_no",
        "inv",
        "inv_no",
        "due_date",
        "amount_due",
        "outstanding_amount",
        "balance_due",
        "total",
        "subtotal",
        "tax",
        "currency",
        "status",
        "customer_id",
        "customer_name",
    ),
    "payments": (
        "payment",
        "payment_id",
        "payment_date",
        "paid_amount",
        "amount_paid",
        "receipt",
        "remittance",
        "reference",
        "paid",
        "amount",
    ),
    "customers": (
        "customer",
        "customer_id",
        "customer_name",
        "client",
        "account_name",
        "account_number",
        "credit_limit",
        "segment",
        "industry",
        "country",
        "name",
        "company",
    ),
    "cash_snapshots": (
        "snapshot_date",
        "opening_balance",
        "closing_balance",
        "cash_in",
        "cash_out",
        "bank_balance",
        "closing_cash",
        "balance",
    ),
    "unpaid_invoice_export": (
        "invoice",
        "invoice_id",
        "invoice_number",
        "customer",
        "customer_name",
        "client",
        "account",
        "due_date",
        "amount_due",
        "balance",
        "open_amount",
        "outstanding",
        "status",
        "unpaid",
        "amount",
        "total",
        "date",
        "terms",
        "aging",
        "days",
        "overdue",
        "paid",
        "remaining",
        "ar",
        "receivable",
        # IBM-specific common headers
        "account_number",
        "account_name",
        "business",
        "company",
        "debtor",
        "credit",
        "debit",
        "current",
        "1_30",
        "31_60",
        "61_90",
        "over_90",
    ),
}

_FILENAME_HINTS: dict[str, tuple[str, ...]] = {
    "invoices": ("invoice", "ar", "receivable"),
    "payments": ("payment", "receipt", "cashapp", "remittance"),
    "customers": ("customer", "client", "account"),
    "cash_snapshots": ("cash", "snapshot", "balance", "bank"),
    "unpaid_invoice_export": ("unpaid", "open_invoice", "outstanding", "aging", "ar", "receivable", "trial_balance", "accounts"),
}


def _normalize_token(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _read_headers_and_count(contents: bytes) -> tuple[list[str], int]:
    text = contents.decode("utf-8-sig", errors="replace")
    reader = csv.reader(StringIO(text))
    rows = list(reader)
    if not rows:
        return [], 0
    headers = [_normalize_token(cell) for cell in rows[0]]
    row_count = max(0, len(rows) - 1)
    return headers, row_count


def detect_file_role(*, filename: str, contents: bytes) -> FileRoleDetection:
    headers, row_count = _read_headers_and_count(contents)
    header_set = set(headers)
    filename_norm = _normalize_token(filename)

    scores: dict[str, float] = {}
    reasons_by_role: dict[str, list[str]] = {}

    for role, aliases in _ROLE_ALIASES.items():
        score = 0.0
        reasons: list[str] = []

        alias_hits = sorted(alias for alias in aliases if alias in header_set)
        if alias_hits:
            # Give more weight per matched header
            score += min(0.80, 0.15 * len(alias_hits))
            reasons.append(f"matched headers: {', '.join(alias_hits[:5])}")

        filename_hits = [hint for hint in _FILENAME_HINTS.get(role, ()) if hint in filename_norm]
        if filename_hits:
            score += min(0.15, 0.05 * len(filename_hits))
            reasons.append(f"filename hints: {', '.join(filename_hits)}")

        # Special handling for unpaid_invoice_export (most common BYOD format)
        if role == "unpaid_invoice_export":
            # Aging bucket headers are strong indicators
            aging_headers = {"current", "1_30", "31_60", "61_90", "over_90", "0_30", "30_60", "60_90", "90_plus"}
            aging_hits = aging_headers & header_set
            if aging_hits:
                score += 0.25
                reasons.append(f"aging buckets detected: {', '.join(sorted(aging_hits)[:3])}")
            
            # Account/customer indicators
            if {"account", "account_number", "account_name", "customer", "customer_name"} & header_set:
                score += 0.10
                reasons.append("account/customer identifiers present")
            
            # Balance/amount headers
            if {"balance", "outstanding", "amount", "total", "due"} & header_set:
                score += 0.10
                reasons.append("balance/amount headers present")
            
            # Date headers
            if {"date", "due_date", "as_of", "invoice_date"} & header_set:
                score += 0.05
                reasons.append("date headers present")

        scores[role] = min(score, 0.99)
        reasons_by_role[role] = reasons

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_role, top_score = ranked[0] if ranked else (None, 0.0)

    # Lower threshold from 0.2 to 0.12 to be more permissive
    if top_score < 0.12:
        return FileRoleDetection(
            role=None,
            confidence=0.0,
            alternatives=ranked[:3],
            reasons=["not enough recognizable headers to infer a reliable file role"],
            headers=headers,
            row_count=row_count,
        )

    return FileRoleDetection(
        role=top_role,
        confidence=round(top_score, 2),
        alternatives=[(role, round(score, 2)) for role, score in ranked[1:4]],
        reasons=reasons_by_role[top_role],
        headers=headers,
        row_count=row_count,
    )
