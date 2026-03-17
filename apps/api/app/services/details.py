from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Customer, Invoice, Payment
from app.services.risk import score_invoice


@dataclass(frozen=True)
class PaymentHistoryItem:
    payment_date: date
    amount: Decimal
    payment_method: str | None
    reference: str | None


@dataclass(frozen=True)
class InvoiceDetailResult:
    invoice_id: str
    customer_id: str
    customer_name: str
    invoice_date: date
    due_date: date
    currency: str
    total_amount: Decimal
    outstanding_amount: Decimal
    amount_paid: Decimal
    status: str
    overdue_days: int
    payment_history: list[PaymentHistoryItem]
    late_payment_probability: Decimal
    risk_bucket: str
    top_reason_codes: list[str]
    recommended_action: str


@dataclass(frozen=True)
class CustomerOpenInvoiceItem:
    invoice_id: str
    total_amount: Decimal
    outstanding_amount: Decimal
    due_date: date
    status: str
    late_payment_probability: Decimal
    risk_bucket: str


@dataclass(frozen=True)
class CustomerDetailResult:
    customer_id: str
    customer_name: str
    industry: str | None
    segment: str | None
    payment_terms_days: int | None
    credit_limit: Decimal | None
    open_exposure: Decimal
    open_invoice_count: int
    overdue_invoice_count: int
    average_days_overdue: float
    late_payment_ratio: float
    top_recommendation: str
    open_invoices: list[CustomerOpenInvoiceItem]


def _resolve_as_of_date(session: Session) -> date:
    latest_payment = session.scalar(select(Payment.payment_date).order_by(Payment.payment_date.desc()).limit(1))
    latest_due_date = session.scalar(select(Invoice.due_date).order_by(Invoice.due_date.desc()).limit(1))
    candidates = [candidate for candidate in [latest_payment, latest_due_date] if candidate is not None]
    return max(candidates) if candidates else date.today()


def get_invoice_detail(session: Session, external_invoice_id: str) -> InvoiceDetailResult | None:
    invoice = session.scalar(
        select(Invoice)
        .options(selectinload(Invoice.customer), selectinload(Invoice.payments))
        .where(Invoice.external_invoice_id == external_invoice_id)
    )
    if invoice is None:
        return None

    as_of = _resolve_as_of_date(session)
    customer = invoice.customer
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)
    payment_history = [
        PaymentHistoryItem(
            payment_date=payment.payment_date,
            amount=payment.amount,
            payment_method=payment.payment_method,
            reference=payment.reference,
        )
        for payment in sorted(invoice.payments, key=lambda payment: payment.payment_date)
    ]
    amount_paid = (invoice.total_amount - invoice.outstanding_amount).quantize(Decimal("0.01"))

    return InvoiceDetailResult(
        invoice_id=invoice.external_invoice_id or str(invoice.id),
        customer_id=customer.external_customer_id or str(customer.id),
        customer_name=customer.name,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        currency=invoice.currency,
        total_amount=invoice.total_amount,
        outstanding_amount=invoice.outstanding_amount,
        amount_paid=amount_paid,
        status=invoice.status,
        overdue_days=max((as_of - invoice.due_date).days, 0),
        payment_history=payment_history,
        late_payment_probability=probability,
        risk_bucket=bucket,
        top_reason_codes=reasons,
        recommended_action=action,
    )


def get_customer_detail(session: Session, external_customer_id: str) -> CustomerDetailResult | None:
    customer = session.scalar(
        select(Customer)
        .options(selectinload(Customer.invoices).selectinload(Invoice.payments))
        .where(Customer.external_customer_id == external_customer_id)
    )
    if customer is None:
        return None

    as_of = _resolve_as_of_date(session)
    open_invoices: list[CustomerOpenInvoiceItem] = []
    overdue_days_accumulator = 0
    overdue_count = 0
    late_like_count = 0
    top_recommendation = "no open receivables follow-up needed"

    for invoice in sorted(customer.invoices, key=lambda inv: inv.due_date):
        overdue_days = max((as_of - invoice.due_date).days, 0)
        if overdue_days > 0:
            overdue_count += 1
            overdue_days_accumulator += overdue_days
        probability, bucket, _reasons, action = score_invoice(invoice, customer, as_of)
        if overdue_days >= 15 or probability >= Decimal("0.55"):
            late_like_count += 1
        if invoice.outstanding_amount > 0:
            open_invoices.append(
                CustomerOpenInvoiceItem(
                    invoice_id=invoice.external_invoice_id or str(invoice.id),
                    total_amount=invoice.total_amount,
                    outstanding_amount=invoice.outstanding_amount,
                    due_date=invoice.due_date,
                    status=invoice.status,
                    late_payment_probability=probability,
                    risk_bucket=bucket,
                )
            )
            top_recommendation = action

    open_exposure = sum((invoice.outstanding_amount for invoice in customer.invoices if invoice.outstanding_amount > 0), Decimal("0.00"))
    invoice_count = len(customer.invoices)
    average_days_overdue = overdue_days_accumulator / overdue_count if overdue_count else 0.0
    late_payment_ratio = late_like_count / invoice_count if invoice_count else 0.0

    return CustomerDetailResult(
        customer_id=customer.external_customer_id or str(customer.id),
        customer_name=customer.name,
        industry=customer.industry,
        segment=customer.segment,
        payment_terms_days=customer.payment_terms_days,
        credit_limit=customer.credit_limit,
        open_exposure=open_exposure.quantize(Decimal("0.01")),
        open_invoice_count=len(open_invoices),
        overdue_invoice_count=overdue_count,
        average_days_overdue=round(average_days_overdue, 2),
        late_payment_ratio=round(late_payment_ratio, 2),
        top_recommendation=top_recommendation if open_invoices else "no open receivables follow-up needed",
        open_invoices=open_invoices,
    )
