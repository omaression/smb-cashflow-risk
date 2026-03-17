from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Customer, Invoice, Payment
from app.services.portfolio import resolve_portfolio_as_of


@dataclass(frozen=True)
class InvoiceFeatureRow:
    invoice_id: str
    customer_id: str
    customer_name: str
    invoice_date: date
    due_date: date
    amount: Decimal
    outstanding_amount: Decimal
    payment_terms_days: int
    invoice_age_days: int
    days_until_due: int
    overdue_days: int
    customer_invoice_count: int
    customer_total_exposure: Decimal
    customer_open_exposure: Decimal
    customer_late_invoice_ratio: float
    customer_average_days_late: float
    payment_count: int
    paid_amount: Decimal
    paid_ratio: float
    is_open: bool
    is_late_15: int


def _payment_summary(invoice: Invoice) -> tuple[int, Decimal, date | None]:
    payments = sorted(invoice.payments, key=lambda payment: payment.payment_date)
    payment_count = len(payments)
    paid_amount = sum((payment.amount for payment in payments), Decimal("0.00"))
    latest_payment_date = payments[-1].payment_date if payments else None
    return payment_count, paid_amount, latest_payment_date


def _historical_customer_lateness(customer: Customer) -> tuple[float, float]:
    settled_invoices = [invoice for invoice in customer.invoices if invoice.outstanding_amount == 0]
    if not settled_invoices:
        return 0.0, 0.0

    late_flags = 0
    days_late_values: list[int] = []

    for invoice in settled_invoices:
        payments = sorted(invoice.payments, key=lambda payment: payment.payment_date)
        if not payments:
            continue
        final_payment_date = payments[-1].payment_date
        days_late = max((final_payment_date - invoice.due_date).days, 0)
        days_late_values.append(days_late)
        if days_late >= 15:
            late_flags += 1

    if not days_late_values:
        return 0.0, 0.0

    return round(late_flags / len(days_late_values), 2), round(sum(days_late_values) / len(days_late_values), 2)


def build_invoice_feature_rows(session: Session, as_of: date | None = None) -> list[InvoiceFeatureRow]:
    resolved_as_of = as_of or resolve_portfolio_as_of(session)
    invoices = list(
        session.scalars(
            select(Invoice)
            .options(selectinload(Invoice.customer).selectinload(Customer.invoices).selectinload(Invoice.payments), selectinload(Invoice.payments))
            .order_by(Invoice.invoice_date.asc(), Invoice.external_invoice_id.asc())
        )
    )

    rows: list[InvoiceFeatureRow] = []

    for invoice in invoices:
        customer = invoice.customer
        payment_count, paid_amount, latest_payment_date = _payment_summary(invoice)
        customer_invoice_count = len(customer.invoices)
        customer_total_exposure = sum((item.total_amount for item in customer.invoices), Decimal("0.00"))
        customer_open_exposure = sum(
            (item.outstanding_amount for item in customer.invoices if item.outstanding_amount > 0), Decimal("0.00")
        )
        customer_late_invoice_ratio, customer_average_days_late = _historical_customer_lateness(customer)

        invoice_age_days = max((resolved_as_of - invoice.invoice_date).days, 0)
        days_until_due = (invoice.due_date - resolved_as_of).days
        overdue_days = max((resolved_as_of - invoice.due_date).days, 0)
        paid_ratio = float((paid_amount / invoice.total_amount).quantize(Decimal("0.01"))) if invoice.total_amount else 0.0
        is_open = invoice.outstanding_amount > 0

        if invoice.outstanding_amount == 0 and latest_payment_date is not None:
            is_late_15 = int((latest_payment_date - invoice.due_date).days >= 15)
        else:
            is_late_15 = int(overdue_days >= 15)

        rows.append(
            InvoiceFeatureRow(
                invoice_id=invoice.external_invoice_id or str(invoice.id),
                customer_id=customer.external_customer_id or str(customer.id),
                customer_name=customer.name,
                invoice_date=invoice.invoice_date,
                due_date=invoice.due_date,
                amount=invoice.total_amount,
                outstanding_amount=invoice.outstanding_amount,
                payment_terms_days=customer.payment_terms_days or invoice.payment_terms_days or 30,
                invoice_age_days=invoice_age_days,
                days_until_due=days_until_due,
                overdue_days=overdue_days,
                customer_invoice_count=customer_invoice_count,
                customer_total_exposure=customer_total_exposure.quantize(Decimal("0.01")),
                customer_open_exposure=customer_open_exposure.quantize(Decimal("0.01")),
                customer_late_invoice_ratio=customer_late_invoice_ratio,
                customer_average_days_late=customer_average_days_late,
                payment_count=payment_count,
                paid_amount=paid_amount.quantize(Decimal("0.01")),
                paid_ratio=paid_ratio,
                is_open=is_open,
                is_late_15=is_late_15,
            )
        )

    return rows
