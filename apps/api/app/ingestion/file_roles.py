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
    ),
    "cash_snapshots": (
        "snapshot_date",
        "opening_balance",
        "closing_balance",
        "cash_in",
        "cash_out",
        "bank_balance",
        "closing_cash",
    ),
    "unpaid_invoice_export": (
        "invoice",
        "invoice_id",
        "customer",
        "customer_name",
        "due_date",
        "amount_due",
        "balance",
        "open_amount",
        "status",
        "unpaid",
        "outstanding",
    ),
}

_FILENAME_HINTS: dict[str, tuple[str, ...]] = {
    "invoices": ("invoice", "ar", "receivable"),
    "payments": ("payment", "receipt", "cashapp", "remittance"),
    "customers": ("customer", "client", "account"),
    "cash_snapshots": ("cash", "snapshot", "balance", "bank"),
    "unpaid_invoice_export": ("unpaid", "open_invoice", "outstanding", "aging"),
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
            score += min(0.75, 0.12 * len(alias_hits))
            reasons.append(f"matched headers: {', '.join(alias_hits[:5])}")

        filename_hits = [hint for hint in _FILENAME_HINTS.get(role, ()) if hint in filename_norm]
        if filename_hits:
            score += min(0.2, 0.08 * len(filename_hits))
            reasons.append(f"filename hints: {', '.join(filename_hits)}")

        # Specific preference: unpaid invoice exports usually have invoice + customer + balance-like fields.
        if role == "unpaid_invoice_export":
            if {"invoice", "due_date"} & header_set and {"customer", "customer_name"} & header_set:
                score += 0.08
                reasons.append("looks like a single-file unpaid invoice export")

        scores[role] = min(score, 0.99)
        reasons_by_role[role] = reasons

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_role, top_score = ranked[0] if ranked else (None, 0.0)

    if top_score < 0.2:
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
