"""
Trial-scoped dashboard endpoints.

Phase 2: Returns actual trial workspace data aggregated from imported records.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.trial_workspace import TrialWorkspace
from app.schemas import DashboardSummaryResponse, InvoiceRiskItem, TopRiskyCustomer
from app.services.trial_summary import build_trial_dashboard_summary, get_trial_invoice_risk_queue

router = APIRouter(prefix="/trial", tags=["trial-dashboard"])


@router.get("/{workspace_id}/summary", response_model=DashboardSummaryResponse)
def get_trial_summary(workspace_id: UUID, db: Session = Depends(get_db)):
    """
    Get dashboard summary for a trial workspace.
    
    Returns actual aggregated data from imported customers, invoices, and payments.
    """
    workspace = db.get(TrialWorkspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    
    # Build summary from trial data
    summary = build_trial_dashboard_summary(db, workspace)
    
    return DashboardSummaryResponse(
        total_ar=float(summary.total_ar),
        overdue_ar=float(summary.overdue_ar),
        open_invoice_count=summary.open_invoice_count,
        risky_invoice_count=summary.risky_invoice_count,
        top_risky_customers=[
            TopRiskyCustomer(
                id=c["id"],
                name=c["name"],
            )
            for c in summary.top_risky_customers
        ],
        projected_cash_balances=summary.projected_cash_balances,
        runtime_model_version="rules-only",
        ml_status_badge="trial-rules",
    )


@router.get("/{workspace_id}/invoices/risk", response_model=list[InvoiceRiskItem])
def get_trial_invoices(workspace_id: UUID, db: Session = Depends(get_db)):
    """
    Get invoice risk queue for a trial workspace.
    
    Returns actual risk-scoredinvoices from imported data.
    """
    workspace = db.get(TrialWorkspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    
    # Get risk queue from trial data
    risk_queue = get_trial_invoice_risk_queue(db, workspace_id)
    
    return [
        InvoiceRiskItem(
            invoice_id=item["invoice_id"],
            customer_name=item["customer_name"],
            amount=item["amount"],
            due_date=item["due_date"],
            overdue_days=item["overdue_days"],
            late_payment_probability=item["late_payment_probability"],
            risk_bucket=item["risk_bucket"],
            top_reason_codes=item["top_reason_codes"],
            recommended_action=item["recommended_action"],
        )
        for item in risk_queue
    ]