from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import InvoiceDetailResponse, InvoiceRiskItem, PaymentHistoryItemResponse
from app.services.details import get_invoice_detail

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/risk", response_model=list[InvoiceRiskItem])
def list_invoice_risk() -> list[InvoiceRiskItem]:
    return [
        InvoiceRiskItem(
            invoice_id="INV-1001",
            customer_name="Northstar Dental Group",
            amount=12720.0,
            due_date=date(2026, 2, 9),
            overdue_days=35,
            late_payment_probability=0.82,
            risk_bucket="high",
            top_reason_codes=["customer_historical_late_ratio", "invoice_overdue_days"],
            recommended_action="send escalation email and call accounts payable",
        ),
        InvoiceRiskItem(
            invoice_id="INV-1003",
            customer_name="Summit Office Interiors",
            amount=9010.0,
            due_date=date(2026, 3, 4),
            overdue_days=11,
            late_payment_probability=0.61,
            risk_bucket="medium",
            top_reason_codes=["recent_payment_slowdown", "customer_concentration_risk"],
            recommended_action="send reminder and monitor for 3 business days",
        ),
    ]


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)) -> InvoiceDetailResponse:
    detail = get_invoice_detail(session=db, external_invoice_id=invoice_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"invoice not found: {invoice_id}")

    return InvoiceDetailResponse(
        invoice_id=detail.invoice_id,
        customer_id=detail.customer_id,
        customer_name=detail.customer_name,
        invoice_date=detail.invoice_date,
        due_date=detail.due_date,
        currency=detail.currency,
        total_amount=float(detail.total_amount),
        outstanding_amount=float(detail.outstanding_amount),
        amount_paid=float(detail.amount_paid),
        status=detail.status,
        overdue_days=detail.overdue_days,
        payment_history=[
            PaymentHistoryItemResponse(
                payment_date=payment.payment_date,
                amount=float(payment.amount),
                payment_method=payment.payment_method,
                reference=payment.reference,
            )
            for payment in detail.payment_history
        ],
        late_payment_probability=float(detail.late_payment_probability),
        risk_bucket=detail.risk_bucket,
        top_reason_codes=detail.top_reason_codes,
        recommended_action=detail.recommended_action,
    )
