from datetime import date

from fastapi import APIRouter

from app.schemas import InvoiceRiskItem

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
