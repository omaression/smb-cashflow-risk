from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models import Customer, Invoice


def _clamp_probability(value: Decimal) -> Decimal:
    if value < Decimal("0.05"):
        return Decimal("0.05")
    if value > Decimal("0.95"):
        return Decimal("0.95")
    return value.quantize(Decimal("0.01"))


def score_invoice(invoice: Invoice, customer: Customer, as_of: date) -> tuple[Decimal, str, list[str], str]:
    overdue_days = max((as_of - invoice.due_date).days, 0)
    payment_terms = customer.payment_terms_days or invoice.payment_terms_days or 30
    concentration_hint = Decimal("0.08") if invoice.total_amount >= Decimal("10000") else Decimal("0.00")
    overdue_component = Decimal(overdue_days) * Decimal("0.012")
    terms_component = Decimal("0.07") if payment_terms >= 45 else Decimal("0.00")
    open_balance_component = Decimal("0.10") if invoice.outstanding_amount == invoice.total_amount else Decimal("0.04")
    base = Decimal("0.28")
    probability = _clamp_probability(base + overdue_component + terms_component + concentration_hint + open_balance_component)

    reasons: list[str] = []
    if overdue_days > 0:
        reasons.append("invoice_overdue_days")
    if payment_terms >= 45:
        reasons.append("extended_payment_terms")
    if invoice.total_amount >= Decimal("10000"):
        reasons.append("customer_concentration_risk")
    if invoice.outstanding_amount == invoice.total_amount:
        reasons.append("no_partial_payments_recorded")

    if probability >= Decimal("0.75"):
        bucket = "high"
        action = "call accounts payable and escalate with a dated payment commitment request"
    elif probability >= Decimal("0.50"):
        bucket = "medium"
        action = "send reminder with invoice backup and monitor within 3 business days"
    else:
        bucket = "low"
        action = "keep in normal collections queue and monitor upcoming due date"

    return probability, bucket, reasons[:3], action
