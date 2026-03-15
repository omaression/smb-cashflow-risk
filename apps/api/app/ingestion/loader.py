import csv
from collections.abc import Callable
from dataclasses import dataclass, field
from io import StringIO
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.validators import CashSnapshotRow, CustomerRow, InvoiceRow, PaymentRow
from app.models import Customer, DailyCashSnapshot, Invoice, Payment


@dataclass
class RowError:
    row_number: int
    message: str


@dataclass
class IngestResult:
    entity_type: str
    imported: int = 0
    updated: int = 0
    rejected: int = 0
    errors: list[RowError] = field(default_factory=list)


def _read_rows(contents: bytes) -> list[dict[str, str]]:
    text = contents.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        return []
    return list(reader)


def _record_error(result: IngestResult, row_number: int, message: str) -> None:
    result.rejected += 1
    result.errors.append(RowError(row_number=row_number, message=message))


def _validate_rows(rows: list[dict[str, str]], schema: type[BaseModel], result: IngestResult) -> list[tuple[int, BaseModel]]:
    validated: list[tuple[int, BaseModel]] = []
    seen_ids: set[str] = set()

    primary_id_field = {
        "CustomerRow": "external_customer_id",
        "InvoiceRow": "external_invoice_id",
        "PaymentRow": "external_payment_id",
    }.get(schema.__name__)

    for offset, row in enumerate(rows, start=2):
        duplicate_key = None
        if primary_id_field:
            raw_value = str(row.get(primary_id_field, "")).strip()
            if raw_value:
                if raw_value in seen_ids:
                    duplicate_key = raw_value
                else:
                    seen_ids.add(raw_value)

        if duplicate_key:
            _record_error(result, offset, f"duplicate external id in file: {duplicate_key}")
            continue

        try:
            validated.append((offset, schema.model_validate(row)))
        except ValidationError as exc:
            _record_error(result, offset, exc.errors()[0]["msg"])

    return validated


def _upsert_customer(session: Session, payload: CustomerRow) -> str:
    existing = session.scalar(select(Customer).where(Customer.external_customer_id == payload.external_customer_id))
    created = existing is None
    customer = existing or Customer(external_customer_id=payload.external_customer_id)
    customer.name = payload.name
    customer.industry = payload.industry
    customer.segment = payload.segment
    customer.country = payload.country
    customer.payment_terms_days = payload.payment_terms_days
    customer.credit_limit = payload.credit_limit
    customer.is_active = payload.is_active
    session.add(customer)
    return "created" if created else "updated"


def _upsert_invoice(session: Session, payload: InvoiceRow) -> str:
    customer = session.scalar(select(Customer).where(Customer.external_customer_id == payload.external_customer_id))
    if not customer:
        raise ValueError(f"customer not found: {payload.external_customer_id}")

    existing = session.scalar(select(Invoice).where(Invoice.external_invoice_id == payload.external_invoice_id))
    created = existing is None
    invoice = existing or Invoice(external_invoice_id=payload.external_invoice_id)
    invoice.customer_id = customer.id
    invoice.invoice_date = payload.invoice_date
    invoice.due_date = payload.due_date
    invoice.currency = payload.currency
    invoice.subtotal_amount = payload.subtotal_amount
    invoice.tax_amount = payload.tax_amount
    invoice.total_amount = payload.total_amount
    invoice.outstanding_amount = payload.outstanding_amount
    invoice.status = payload.status
    invoice.payment_terms_days = payload.payment_terms_days
    session.add(invoice)
    return "created" if created else "updated"


def _apply_invoice_payment_rollup(session: Session, invoice: Invoice) -> None:
    payments = list(session.scalars(select(Payment).where(Payment.invoice_id == invoice.id)))
    paid_amount = sum(payment.amount for payment in payments)
    outstanding = invoice.total_amount - paid_amount
    if outstanding < 0:
        raise ValueError(f"payments exceed invoice total for {invoice.external_invoice_id}")
    invoice.outstanding_amount = outstanding
    if outstanding == 0:
        invoice.status = "paid"
    elif paid_amount > 0:
        invoice.status = "partially_paid"
    elif invoice.status == "paid":
        invoice.status = "sent"


def _upsert_payment(session: Session, payload: PaymentRow) -> str:
    invoice = session.scalar(select(Invoice).where(Invoice.external_invoice_id == payload.external_invoice_id))
    if not invoice:
        raise ValueError(f"invoice not found: {payload.external_invoice_id}")

    customer = session.scalar(select(Customer).where(Customer.external_customer_id == payload.external_customer_id))
    if not customer:
        raise ValueError(f"customer not found: {payload.external_customer_id}")
    if invoice.customer_id != customer.id:
        raise ValueError("payment customer does not match invoice customer")
    if payload.payment_date < invoice.invoice_date:
        raise ValueError("payment_date must be on or after invoice_date")

    existing = session.scalar(select(Payment).where(Payment.external_payment_id == payload.external_payment_id))
    created = existing is None
    payment = existing or Payment(external_payment_id=payload.external_payment_id)
    payment.invoice_id = invoice.id
    payment.customer_id = customer.id
    payment.payment_date = payload.payment_date
    payment.amount = payload.amount
    payment.currency = payload.currency
    payment.payment_method = payload.payment_method
    payment.reference = payload.reference
    session.add(payment)
    session.flush()
    _apply_invoice_payment_rollup(session, invoice)
    return "created" if created else "updated"


def _upsert_cash_snapshot(session: Session, payload: CashSnapshotRow) -> str:
    existing = session.scalar(
        select(DailyCashSnapshot).where(
            DailyCashSnapshot.snapshot_date == payload.snapshot_date,
            DailyCashSnapshot.currency == payload.currency,
        )
    )
    created = existing is None
    snapshot = existing or DailyCashSnapshot(snapshot_date=payload.snapshot_date, currency=payload.currency)
    snapshot.opening_balance = payload.opening_balance
    snapshot.cash_in = payload.cash_in
    snapshot.cash_out = payload.cash_out
    snapshot.closing_balance = payload.closing_balance
    session.add(snapshot)
    return "created" if created else "updated"


def ingest_csv_file(entity_type: str, contents: bytes, session: Session) -> IngestResult:
    handlers: dict[str, tuple[type[BaseModel], Callable[[Session, Any], str]]] = {
        "customers": (CustomerRow, _upsert_customer),
        "invoices": (InvoiceRow, _upsert_invoice),
        "payments": (PaymentRow, _upsert_payment),
        "cash_snapshots": (CashSnapshotRow, _upsert_cash_snapshot),
    }
    if entity_type not in handlers:
        raise ValueError(f"unsupported entity_type: {entity_type}")

    rows = _read_rows(contents)
    result = IngestResult(entity_type=entity_type)
    schema, handler = handlers[entity_type]
    validated = _validate_rows(rows, schema, result)

    for row_number, payload in validated:
        try:
            action = handler(session, payload)
            if action == "created":
                result.imported += 1
            else:
                result.updated += 1
        except ValueError as exc:
            session.rollback()
            _record_error(result, row_number, str(exc))

    session.commit()
    return result
