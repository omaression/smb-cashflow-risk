from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldMapping:
    canonical_field: str
    source_field: str | None
    confidence: float
    required: bool
    resolved: bool
    alternatives: list[str]


@dataclass(frozen=True)
class RoleMappingResult:
    role: str
    confidence: float
    field_mappings: list[FieldMapping]
    required_missing: list[str]
    ambiguity_warnings: list[str]


# Canonical fields by role with required flags
_CANONICAL_FIELDS: dict[str, dict[str, bool]] = {
    "invoices": {
        "external_invoice_id": True,
        "external_customer_id": True,
        "invoice_date": True,
        "due_date": True,
        "total_amount": True,
        "outstanding_amount": False,
        "currency": False,
        "status": False,
        "payment_terms_days": False,
    },
    "payments": {
        "external_payment_id": False,
        "external_invoice_id": True,
        "external_customer_id": True,
        "payment_date": True,
        "amount": True,
        "currency": False,
        "payment_method": False,
        "reference": False,
    },
    "customers": {
        "external_customer_id": True,
        "name": True,
        "industry": False,
        "segment": False,
        "country": False,
        "payment_terms_days": False,
        "credit_limit": False,
    },
    "cash_snapshots": {
        "snapshot_date": True,
        "currency": True,
        "opening_balance": True,
        "cash_in": False,
        "cash_out": False,
        "closing_balance": True,
    },
    "unpaid_invoice_export": {
        "external_invoice_id": True,
        "customer_name": True,
        "invoice_date": True,
        "due_date": True,
        "outstanding_amount": True,
        "currency": False,
        "status": False,
    },
}

# Field aliases by role: map heuristic aliases to canonical fields
_FIELD_ALIASES: dict[str, dict[str, str]] = {
    "invoices": {
        "invoice": "external_invoice_id",
        "invoice_id": "external_invoice_id",
        "invoice_no": "external_invoice_id",
        "invoice_number": "external_invoice_id",
        "inv": "external_invoice_id",
        "inv_no": "external_invoice_id",
        "customer_id": "external_customer_id",
        "customer": "external_customer_id",
        "client": "external_customer_id",
        "client_id": "external_customer_id",
        "customer_name": "customer_name",
        "inv_date": "invoice_date",
        "date": "invoice_date",
        "invoice_date": "invoice_date",
        "due": "due_date",
        "due_date": "due_date",
        "due_dt": "due_date",
        "total": "total_amount",
        "total_amount": "total_amount",
        "amount": "total_amount",
        "subtotal": "subtotal_amount",
        "subtotal_amount": "subtotal_amount",
        "balance": "outstanding_amount",
        "outstanding": "outstanding_amount",
        "outstanding_amount": "outstanding_amount",
        "amount_due": "outstanding_amount",
        "open_amount": "outstanding_amount",
        "balance_due": "outstanding_amount",
        "currency": "currency",
        "ccy": "currency",
        "status": "status",
        "invoice_status": "status",
    },
    "payments": {
        "payment": "external_payment_id",
        "payment_id": "external_payment_id",
        "payment_no": "external_payment_id",
        "pay_id": "external_payment_id",
        "receipt": "external_payment_id",
        "receipt_no": "external_payment_id",
        "remittance_no": "external_payment_id",
        "invoice": "external_invoice_id",
        "invoice_id": "external_invoice_id",
        "invoice_no": "external_invoice_id",
        "customer": "external_customer_id",
        "customer_id": "external_customer_id",
        "client": "external_customer_id",
        "client_id": "external_customer_id",
        "paid_date": "payment_date",
        "payment_date": "payment_date",
        "date": "payment_date",
        "paid": "amount",
        "amount": "amount",
        "paid_amount": "amount",
        "currency": "currency",
        "ccy": "currency",
        "method": "payment_method",
        "payment_method": "payment_method",
        "ref": "reference",
        "reference": "reference",
        "memo": "reference",
    },
    "customers": {
        "customer": "external_customer_id",
        "customer_id": "external_customer_id",
        "customer_no": "external_customer_id",
        "client": "external_customer_id",
        "client_id": "external_customer_id",
        "acct": "external_customer_id",
        "account_id": "external_customer_id",
        "name": "name",
        "customer_name": "name",
        "client_name": "name",
        "company": "name",
        "industry": "industry",
        "segment": "segment",
        "country": "country",
        "terms": "payment_terms_days",
        "payment_terms": "payment_terms_days",
        "credit_limit": "credit_limit",
        "limit": "credit_limit",
    },
    "cash_snapshots": {
        "date": "snapshot_date",
        "snapshot_date": "snapshot_date",
        "as_of": "snapshot_date",
        "currency": "currency",
        "ccy": "currency",
        "opening": "opening_balance",
        "opening_balance": "opening_balance",
        "start_balance": "opening_balance",
        "cash_in": "cash_in",
        "inflow": "cash_in",
        "cash_out": "cash_out",
        "outflow": "cash_out",
        "closing": "closing_balance",
        "closing_balance": "closing_balance",
        "end_balance": "closing_balance",
        "balance": "closing_balance",
    },
    "unpaid_invoice_export": {
        "invoice": "external_invoice_id",
        "invoice_id": "external_invoice_id",
        "invoice_no": "external_invoice_id",
        "inv": "external_invoice_id",
        "inv_no": "external_invoice_id",
        "customer": "customer_name",
        "customer_name": "customer_name",
        "client": "customer_name",
        "client_name": "customer_name",
        "name": "customer_name",
        "inv_date": "invoice_date",
        "date": "invoice_date",
        "invoice_date": "invoice_date",
        "due": "due_date",
        "due_date": "due_date",
        "due_dt": "due_date",
        "amount": "outstanding_amount",
        "balance": "outstanding_amount",
        "outstanding": "outstanding_amount",
        "outstanding_amount": "outstanding_amount",
        "amount_due": "outstanding_amount",
        "open_amount": "outstanding_amount",
        "balance_due": "outstanding_amount",
        "currency": "currency",
        "ccy": "currency",
        "status": "status",
        "invoice_status": "status",
    },
}


def suggest_field_mappings(*, role: str, headers: list[str]) -> RoleMappingResult:
    """Infer field mappings for a detected role given a list of normalized headers."""
    canonical_spec = _CANONICAL_FIELDS.get(role, {})
    aliases = _FIELD_ALIASES.get(role, {})

    normalized_headers = [h.strip().lower().replace(" ", "_").replace("-", "_") for h in headers]
    header_set = set(normalized_headers)

    field_mappings: list[FieldMapping] = []
    required_missing: list[str] = []
    ambiguity_warnings: list[str] = []

    for canonical_field, required in canonical_spec.items():
        candidates = [
            (source_field, aliases.get(source_field))
            for source_field in header_set
            if aliases.get(source_field) == canonical_field
        ]

        if len(candidates) == 0:
            field_mappings.append(
                FieldMapping(
                    canonical_field=canonical_field,
                    source_field=None,
                    confidence=0.0,
                    required=required,
                    resolved=False,
                    alternatives=[],
                )
            )
            if required:
                required_missing.append(canonical_field)
            continue

        if len(candidates) == 1:
            source_field, _ = candidates[0]
            field_mappings.append(
                FieldMapping(
                    canonical_field=canonical_field,
                    source_field=source_field,
                    confidence=0.85,
                    required=required,
                    resolved=True,
                    alternatives=[],
                )
            )
            continue

        # Multiple candidates for same canonical field
        best_source = sorted(candidates, key=lambda pair: -len(pair[0]))[0][0]
        alternatives = [src for src, _ in candidates if src != best_source]
        field_mappings.append(
            FieldMapping(
                canonical_field=canonical_field,
                source_field=best_source,
                confidence=0.55,
                required=required,
                resolved=False,
                alternatives=alternatives,
            )
        )
        ambiguity_warnings.append(
            f"Multiple columns map to '{canonical_field}': {', '.join([best_source] + alternatives[:3])}."
        )

    confidence = 1.0 if not required_missing else max(0.0, 1.0 - 0.2 * len(required_missing))
    confidence = min(confidence, 0.95) if ambiguity_warnings else confidence

    return RoleMappingResult(
        role=role,
        confidence=round(confidence, 2),
        field_mappings=field_mappings,
        required_missing=required_missing,
        ambiguity_warnings=ambiguity_warnings,
    )