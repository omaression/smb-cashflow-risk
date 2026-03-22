"""
Trial-scoped dashboard endpoints.

Phase 1: Returns demo data tagged with workspace metadata.
Phase 2: Will aggregate actual trial workspace data.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.trial_workspace import TrialWorkspace
from app.schemas import DashboardSummaryResponse, InvoiceRiskItem

router = APIRouter(prefix="/trial", tags=["trial-dashboard"])


@router.get("/{workspace_id}/summary", response_model=DashboardSummaryResponse)
def get_trial_summary(workspace_id: UUID, db: Session = Depends(get_db)):
    """
    Get dashboard summary for a trial workspace.
    
    Phase 1: Returns seeded demo data with workspace metadata.
    Phase 2: Will return actual trial workspace data.
    """
    workspace = db.get(TrialWorkspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    
    # STUB: Return demo data for now, tagged with workspace info
    # Full implementation in Phase 2 will aggregate trial data
    from app.services.portfolio import build_dashboard_summary
    from app.services.model_version import CURRENT_MODEL_VERSION
    from app.schemas import TopRiskyCustomer
    
    summary = build_dashboard_summary(db)
    
    return DashboardSummaryResponse(
        total_ar=float(summary.total_ar),
        overdue_ar=float(summary.overdue_ar),
        open_invoice_count=summary.open_invoice_count,
        risky_invoice_count=summary.risky_invoice_count,
        top_risky_customers=[TopRiskyCustomer(**c) for c in summary.top_risky_customers],
        projected_cash_balances=summary.projected_cash_balances,
        runtime_model_version=CURRENT_MODEL_VERSION.version,
        ml_status_badge="rules-only",
        # Note: In Phase 2, will add workspace-specific metadata fields
    )


@router.get("/{workspace_id}/invoices/risk", response_model=list[InvoiceRiskItem])
def get_trial_invoices(workspace_id: UUID, db: Session = Depends(get_db)):
    """
    Get invoice risk queue for a trial workspace.
    
    Phase 1: Returns seeded demo invoices.
    Phase 2: Will return trial-scoped invoices.
    """
    workspace = db.get(TrialWorkspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    
    # STUB: Return demo invoices for now
    from app.services.portfolio import get_risk_queue
    
    risk_queue = get_risk_queue(db)
    
    return [
        InvoiceRiskItem(
            invoice_id=inv.invoice_id,
            customer_name=inv.customer_name,
            amount=float(inv.amount),
            due_date=inv.due_date,
            overdue_days=inv.overdue_days,
            late_payment_probability=float(inv.late_payment_probability),
            risk_bucket=inv.risk_bucket,
            top_reason_codes=inv.top_reason_codes,
            recommended_action=inv.recommended_action,
        )
        for inv in risk_queue
    ]