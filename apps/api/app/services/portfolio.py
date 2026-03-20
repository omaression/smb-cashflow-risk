from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Customer, DailyCashSnapshot, Invoice, Payment
from app.services.forecast import SUPPORTED_HORIZONS, build_cash_forecast
from app.services.risk import score_invoice

OPEN_INVOICE_STATUSES = {"sent", "partially_paid"}


@dataclass(frozen=True)
class RankedInvoice:
    invoice_id: str
    customer_id: str
    customer_name: str
    amount: Decimal
    due_date: date
    overdue_days: int
    late_payment_probability: Decimal
    risk_bucket: str
    top_reason_codes: list[str]
    recommended_action: str
    priority_score: Decimal


@dataclass(frozen=True)
class DashboardSummary:
    total_ar: Decimal
    overdue_ar: Decimal
    open_invoice_count: int
    risky_invoice_count: int
    top_risky_customers: list[dict[str, str]]
    projected_cash_balances: dict[str, float]


def resolve_portfolio_as_of(session: Session) -> date:
    latest_due_date = session.scalar(select(Invoice.due_date).order_by(Invoice.due_date.desc()).limit(1))
    latest_payment_date = session.scalar(select(Payment.payment_date).order_by(Payment.payment_date.desc()).limit(1))
    latest_snapshot_date = session.scalar(
        select(DailyCashSnapshot.snapshot_date).order_by(DailyCashSnapshot.snapshot_date.desc()).limit(1)
    )
    candidates = [candidate for candidate in [latest_due_date, latest_payment_date, latest_snapshot_date] if candidate is not None]
    return max(candidates) if candidates else date.today()


def _open_invoices(session: Session) -> list[Invoice]:
    return list(
        session.scalars(
            select(Invoice)
            .options(selectinload(Invoice.customer))
            .where(Invoice.status.in_(OPEN_INVOICE_STATUSES), Invoice.outstanding_amount > 0)
            .order_by(Invoice.due_date.asc(), Invoice.external_invoice_id.asc())
        )
    )


def _priority_score(invoice: Invoice, probability: Decimal, overdue_days: int) -> Decimal:
    amount_factor = invoice.outstanding_amount / Decimal("1000")
    overdue_factor = Decimal(min(overdue_days, 60)) / Decimal("10")
    return (probability * amount_factor + overdue_factor).quantize(Decimal("0.01"))


def rank_open_invoices(session: Session) -> list[RankedInvoice]:
    as_of = resolve_portfolio_as_of(session)
    ranked: list[RankedInvoice] = []

    for invoice in _open_invoices(session):
        customer: Customer = invoice.customer
        probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)
        overdue_days = max((as_of - invoice.due_date).days, 0)
        ranked.append(
            RankedInvoice(
                invoice_id=invoice.external_invoice_id or str(invoice.id),
                customer_id=customer.external_customer_id or str(customer.id),
                customer_name=customer.name,
                amount=invoice.outstanding_amount,
                due_date=invoice.due_date,
                overdue_days=overdue_days,
                late_payment_probability=probability,
                risk_bucket=bucket,
                top_reason_codes=reasons,
                recommended_action=action,
                priority_score=_priority_score(invoice, probability=probability, overdue_days=overdue_days),
            )
        )

    return sorted(ranked, key=lambda item: (item.priority_score, item.late_payment_probability, item.amount), reverse=True)


def build_dashboard_summary(session: Session) -> DashboardSummary:
    ranked = rank_open_invoices(session)
    total_ar = sum((item.amount for item in ranked), Decimal("0.00"))
    overdue_ar = sum((item.amount for item in ranked if item.overdue_days > 0), Decimal("0.00"))
    risky_invoice_count = sum(1 for item in ranked if item.risk_bucket in {"medium", "high"})

    seen_customers: set[str] = set()
    top_risky_customers: list[dict[str, str]] = []
    for item in ranked:
        if item.risk_bucket in {"medium", "high"} and item.customer_id not in seen_customers:
            seen_customers.add(item.customer_id)
            top_risky_customers.append({"id": item.customer_id, "name": item.customer_name})
        if len(top_risky_customers) == 3:
            break

    projected_cash_balances: dict[str, float] = {}
    for horizon in sorted(SUPPORTED_HORIZONS):
        forecast = build_cash_forecast(session, horizon_days=horizon, scenario="base")
        projected_cash_balances[str(horizon)] = float(forecast.series[0].projected_balance)

    return DashboardSummary(
        total_ar=total_ar.quantize(Decimal("0.01")),
        overdue_ar=overdue_ar.quantize(Decimal("0.01")),
        open_invoice_count=len(ranked),
        risky_invoice_count=risky_invoice_count,
        top_risky_customers=top_risky_customers,
        projected_cash_balances=projected_cash_balances,
    )
