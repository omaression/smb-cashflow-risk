from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import InvoiceDetailResponse, InvoiceRiskItem, PaymentHistoryItemResponse
from app.services.details import get_invoice_detail
from app.services.portfolio import rank_open_invoices

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/risk", response_model=list[InvoiceRiskItem])
def list_invoice_risk(db: Session = Depends(get_db)) -> list[InvoiceRiskItem]:
    ranked = rank_open_invoices(db)
    return [
        InvoiceRiskItem(
            invoice_id=item.invoice_id,
            customer_name=item.customer_name,
            amount=float(item.amount),
            due_date=item.due_date,
            overdue_days=item.overdue_days,
            late_payment_probability=float(item.late_payment_probability),
            risk_bucket=item.risk_bucket,
            top_reason_codes=item.top_reason_codes,
            recommended_action=item.recommended_action,
        )
        for item in ranked
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
