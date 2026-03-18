from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CustomerDetailResponse, CustomerOpenInvoiceResponse
from app.services.details import get_customer_detail

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)) -> CustomerDetailResponse:
    detail = get_customer_detail(session=db, external_customer_id=customer_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"customer not found: {customer_id}")

    return CustomerDetailResponse(
        customer_id=detail.customer_id,
        customer_name=detail.customer_name,
        industry=detail.industry,
        segment=detail.segment,
        payment_terms_days=detail.payment_terms_days,
        credit_limit=float(detail.credit_limit) if detail.credit_limit is not None else None,
        open_exposure=float(detail.open_exposure),
        open_invoice_count=detail.open_invoice_count,
        overdue_invoice_count=detail.overdue_invoice_count,
        average_days_overdue=detail.average_days_overdue,
        late_payment_ratio=detail.late_payment_ratio,
        top_recommendation=detail.top_recommendation,
        open_invoices=[
            CustomerOpenInvoiceResponse(
                invoice_id=invoice.invoice_id,
                total_amount=float(invoice.total_amount),
                outstanding_amount=float(invoice.outstanding_amount),
                due_date=invoice.due_date,
                status=invoice.status,
                late_payment_probability=float(invoice.late_payment_probability),
                risk_bucket=invoice.risk_bucket,
            )
            for invoice in detail.open_invoices
        ],
    )
