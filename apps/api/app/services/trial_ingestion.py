"""
Trial workspace data ingestion.

Processes ImportFile records and creates trial-scoped customer, invoice,
payment, and cash snapshot data for BYOD workspaces.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.validators import CashSnapshotRow, CustomerRow, InvoiceRow, PaymentRow
from app.models.trial_data import TrialCashSnapshot, TrialCustomer, TrialInvoice, TrialPayment
from app.models.trial_workspace import ImportFile, TrialWorkspace


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


def _record_error(result: IngestResult, row_number: int, message: str) -> None:
    result.rejected += 1
    result.errors.append(RowError(row_number=row_number, message=message))


def _apply_field_mapping(row: dict[str, str], mapping_json: str) -> dict[str, str]:
    """
    Apply field mapping from mapping_json to transform source columns to canonical fields.
    
    mapping_json format:
    {
        "customer_name": {"source": "Client Name", "confidence": 0.95, ...},
        ...
    }
    """
    mapping = json.loads(mapping_json)
    result = {}
    for canonical_field, field_info in mapping.items():
        if canonical_field == "_alternatives":
            continue
        source_field = field_info.get("source")
        if source_field and source_field in row:
            result[canonical_field] = row[source_field]
    return result


def _validate_rows(
    rows: list[dict[str, str]], 
    schema: type[BaseModel], 
    result: IngestResult,
    mapping_json: str | None = None,
) -> list[tuple[int, BaseModel]]:
    validated: list[tuple[int, BaseModel]] = []
    seen_ids: set[str] = set()

    primary_id_field = {
        "CustomerRow": "external_customer_id",
        "InvoiceRow": "external_invoice_id",
        "PaymentRow": "external_payment_id",
    }.get(schema.__name__)

    for offset, row in enumerate(rows, start=2):
        # Apply field mapping if provided
        if mapping_json:
            row = _apply_field_mapping(row, mapping_json)
        
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


def _upsert_trial_customer(session: Session, workspace_id: UUID, payload: CustomerRow) -> str:
    existing = session.scalar(
        select(TrialCustomer).where(
            TrialCustomer.workspace_id == workspace_id,
            TrialCustomer.external_customer_id == payload.external_customer_id,
        )
    )
    created = existing is None
    customer = existing or TrialCustomer(workspace_id=workspace_id, external_customer_id=payload.external_customer_id)
    customer.name = payload.name
    customer.industry = payload.industry
    customer.segment = payload.segment
    customer.country = payload.country
    customer.payment_terms_days = payload.payment_terms_days
    customer.credit_limit = payload.credit_limit
    customer.is_active = payload.is_active
    session.add(customer)
    return "created" if created else "updated"


def _upsert_trial_invoice(session: Session, workspace_id: UUID, payload: InvoiceRow) -> str:
    customer = session.scalar(
        select(TrialCustomer).where(
            TrialCustomer.workspace_id == workspace_id,
            TrialCustomer.external_customer_id == payload.external_customer_id,
        )
    )
    if not customer:
        raise ValueError(f"customer not found: {payload.external_customer_id}")

    existing = session.scalar(
        select(TrialInvoice).where(
            TrialInvoice.workspace_id == workspace_id,
            TrialInvoice.external_invoice_id == payload.external_invoice_id,
        )
    )
    created = existing is None
    invoice = existing or TrialInvoice(workspace_id=workspace_id, external_invoice_id=payload.external_invoice_id)
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


def _apply_trial_invoice_payment_rollup(session: Session, invoice: TrialInvoice) -> None:
    payments = list(session.scalars(select(TrialPayment).where(TrialPayment.invoice_id == invoice.id)))
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


def _upsert_trial_payment(session: Session, workspace_id: UUID, payload: PaymentRow) -> str:
    invoice = session.scalar(
        select(TrialInvoice).where(
            TrialInvoice.workspace_id == workspace_id,
            TrialInvoice.external_invoice_id == payload.external_invoice_id,
        )
    )
    if not invoice:
        raise ValueError(f"invoice not found: {payload.external_invoice_id}")

    customer = session.scalar(
        select(TrialCustomer).where(
            TrialCustomer.workspace_id == workspace_id,
            TrialCustomer.external_customer_id == payload.external_customer_id,
        )
    )
    if not customer:
        raise ValueError(f"customer not found: {payload.external_customer_id}")
    if invoice.customer_id != customer.id:
        raise ValueError("payment customer does not match invoice customer")
    if payload.payment_date < invoice.invoice_date:
        raise ValueError("payment_date must be on or after invoice_date")

    existing = session.scalar(
        select(TrialPayment).where(
            TrialPayment.workspace_id == workspace_id,
            TrialPayment.external_payment_id == payload.external_payment_id,
        )
    )
    created = existing is None
    payment = existing or TrialPayment(workspace_id=workspace_id, external_payment_id=payload.external_payment_id)
    payment.invoice_id = invoice.id
    payment.customer_id = customer.id
    payment.payment_date = payload.payment_date
    payment.amount = payload.amount
    payment.payment_method = payload.payment_method
    session.add(payment)
    session.flush()
    _apply_trial_invoice_payment_rollup(session, invoice)
    return "created" if created else "updated"


def _upsert_trial_cash_snapshot(session: Session, workspace_id: UUID, payload: Any) -> str:
    # Cash snapshots are less common in BYOD, but handle them if provided
    existing = session.scalar(
        select(TrialCashSnapshot).where(
            TrialCashSnapshot.workspace_id == workspace_id,
            TrialCashSnapshot.snapshot_date == payload.snapshot_date,
        )
    )
    created = existing is None
    snapshot = existing or TrialCashSnapshot(workspace_id=workspace_id, snapshot_date=payload.snapshot_date)
    snapshot.balance = payload.closing_balance
    session.add(snapshot)
    return "created" if created else "updated"


def ingest_trial_file(
    workspace_id: UUID,
    entity_type: str,
    rows: list[dict[str, str]],
    session: Session,
    mapping_json: str | None = None,
) -> IngestResult:
    """
    Ingest parsed row data into trial-scoped data tables.
    
    Args:
        workspace_id: The trial workspace UUID
        entity_type: One of "customers", "invoices", "payments", "cash_snapshots", "unpaid_invoices"
        rows: Parsed row data (list of dictionaries)
        session: Database session
        mapping_json: Optional field mapping JSON from ImportFile.mapping_json
        
    Returns:
        IngestResult with import counts and any errors
    """
    handlers: dict[str, tuple[type[BaseModel], Any]] = {
        "customers": (CustomerRow, lambda s, w, p: _upsert_trial_customer(s, w, p)),
        "invoices": (InvoiceRow, lambda s, w, p: _upsert_trial_invoice(s, w, p)),
        "payments": (PaymentRow, lambda s, w, p: _upsert_trial_payment(s, w, p)),
        "cash_snapshots": (CashSnapshotRow, lambda s, w, p: _upsert_trial_cash_snapshot(s, w, p)),
        # Single-file unpaid invoice export maps to invoices
        "unpaid_invoices": (InvoiceRow, lambda s, w, p: _upsert_trial_invoice(s, w, p)),
        "unpaid_invoice_export": (InvoiceRow, lambda s, w, p: _upsert_trial_invoice(s, w, p)),
    }
    if entity_type not in handlers:
        raise ValueError(f"unsupported entity_type: {entity_type}")

    result = IngestResult(entity_type=entity_type)
    schema, handler = handlers[entity_type]
    validated = _validate_rows(rows, schema, result, mapping_json)

    for row_number, payload in validated:
        try:
            action = handler(session, workspace_id, payload)
            if action == "created":
                result.imported += 1
            else:
                result.updated += 1
        except ValueError as exc:
            session.rollback()
            _record_error(result, row_number, str(exc))

    return result


def finalize_trial_workspace(session: Session, workspace_id: UUID) -> dict[str, IngestResult]:
    """
    Process all import files in a workspace and materialize trial data.
    
    Args:
        session: Database session
        workspace_id: The trial workspace UUID
        
    Returns:
        Dict mapping entity type to IngestResult
    """
    workspace = session.get(TrialWorkspace, workspace_id)
    if not workspace:
        raise ValueError(f"Workspace not found: {workspace_id}")
    
    results: dict[str, IngestResult] = {}
    
    # Map detected roles to entity types and processing order
    role_to_entity = {
        "customers": "customers",
        "invoices": "invoices",
        "payments": "payments",
        "cash_snapshots": "cash_snapshots",
        "unpaid_invoices": "invoices",
        "unpaid_invoice_export": "invoices",
    }
    
    # Processing order: customers first (invoices depend on them), then invoices, payments, snapshots
    processing_order = ["customers", "invoices", "payments", "cash_snapshots"]
    pending_files: dict[str, list[tuple[ImportFile, list[dict[str, str]]]]] = {et: [] for et in processing_order}
    
    # Collect all import files and their parsed data
    for job in workspace.import_jobs:
        for import_file in job.files:
            if not import_file.raw_rows_json:
                continue
            detected_role = import_file.detected_role
            if not detected_role or detected_role == "unknown":
                continue
            
            entity_type = role_to_entity.get(detected_role)
            if not entity_type:
                continue
            
            try:
                rows = json.loads(import_file.raw_rows_json)
                if entity_type in pending_files:
                    pending_files[entity_type].append((import_file, rows))
            except json.JSONDecodeError:
                continue
    
    # Process in dependency order
    for entity_type in processing_order:
        for import_file, rows in pending_files.get(entity_type, []):
            result = ingest_trial_file(
                workspace_id=workspace_id,
                entity_type=entity_type,
                rows=rows,
                session=session,
                mapping_json=import_file.mapping_json,
            )
            if entity_type in results:
                # Merge results if multiple files for same entity type
                existing = results[entity_type]
                existing.imported += result.imported
                existing.updated += result.updated
                existing.rejected += result.rejected
                existing.errors.extend(result.errors)
            else:
                results[entity_type] = result
    
    # Update workspace status
    workspace.status = "active"
    workspace.imported_at = datetime.utcnow()
    session.commit()
    
    return results