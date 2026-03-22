"""
Trial workspace summary building logic.

Builds dashboard summaries from trial-scoped data (TrialCustomer, TrialInvoice, etc.)
for BYOD workspaces.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.trial_data import TrialCashSnapshot, TrialCustomer, TrialInvoice, TrialPayment
from app.models.trial_workspace import TrialWorkspace
from app.services.risk import score_invoice


@dataclass(frozen=True)
class TrialDashboardSummary:
    """Summary data for a trial workspace dashboard."""
    
    workspace_id: str
    workspace_label: str
    total_ar: Decimal
    overdue_ar: Decimal
    open_invoice_count: int
    risky_invoice_count: int
    top_risky_customers: list[dict[str, Any]]
    projected_cash_balances: dict[str, float]
    data_quality_score: Decimal | None
    confidence_score: Decimal | None


def build_trial_dashboard_summary(session: Session, workspace: TrialWorkspace) -> TrialDashboardSummary:
    """
    Build a dashboard summary for a trial workspace using actual imported data.
    
    Args:
        session: Database session
        workspace: The trial workspace
        
    Returns:
        TrialDashboardSummary with computed metrics
    """
    workspace_id = workspace.id
    
    # Get all open invoices for this workspace
    invoices = list(
        session.scalars(
            select(TrialInvoice)
            .options(selectinload(TrialInvoice.customer))
            .where(
                TrialInvoice.workspace_id == workspace_id,
                TrialInvoice.outstanding_amount > 0,
            )
            .order_by(TrialInvoice.due_date.asc())
        )
    )
    
    # Calculate AR totals
    total_ar = sum(inv.outstanding_amount for inv in invoices)
    today = date.today()
    overdue_ar = sum(
        inv.outstanding_amount for inv in invoices
        if inv.due_date < today
    )
    
    # Score invoices for risk
    scored_invoices = []
    for inv in invoices:
        risk_score = score_invoice(
            amount=float(inv.outstanding_amount),
            due_date=inv.due_date,
            customer_segment=inv.customer.segment if inv.customer else None,
            customer_industry=inv.customer.industry if inv.customer else None,
        )
        scored_invoices.append((inv, risk_score))
    
    # Count risky invoices (late_payment_probability >= 0.7 or overdue)
    risky_invoice_count = sum(
        1 for inv, score in scored_invoices
        if score.get("late_payment_probability", 0) >= 0.7 or inv.due_date < today
    )
    
    # Get top risky customers by invoice count and amount
    customer_risk: dict[str, dict[str, Any]] = {}
    for inv, score in scored_invoices:
        customer_name = inv.customer.name if inv.customer else "Unknown"
        if customer_name not in customer_risk:
            customer_risk[customer_name] = {
                "customer_name": customer_name,
                "invoice_count": 0,
                "total_amount": Decimal("0"),
                "overdue_amount": Decimal("0"),
                "avg_risk_score": 0.0,
                "risk_scores": [],
            }
        customer_risk[customer_name]["invoice_count"] += 1
        customer_risk[customer_name]["total_amount"] += inv.outstanding_amount
        if inv.due_date < today:
            customer_risk[customer_name]["overdue_amount"] += inv.outstanding_amount
        customer_risk[customer_name]["risk_scores"].append(score.get("late_payment_probability", 0))
    
    # Calculate average risk score and sort
    for name in customer_risk:
        scores = customer_risk[name]["risk_scores"]
        customer_risk[name]["avg_risk_score"] = sum(scores) / len(scores) if scores else 0
    
    top_risky = sorted(
        customer_risk.values(),
        key=lambda c: (c["overdue_amount"], c["avg_risk_score"]),
        reverse=True,
    )[:5]
    
    top_risky_customers = [
        {
            "customer_name": c["customer_name"],
            "invoice_count": c["invoice_count"],
            "total_amount": float(c["total_amount"]),
            "overdue_amount": float(c["overdue_amount"]),
            "avg_risk_score": round(c["avg_risk_score"], 2),
        }
        for c in top_risky
    ]
    
    # Build cash projection from trial cash snapshots
    snapshots = list(
        session.scalars(
            select(TrialCashSnapshot)
            .where(TrialCashSnapshot.workspace_id == workspace_id)
            .order_by(TrialCashSnapshot.snapshot_date.asc())
            .limit(90)
        )
    )
    
    projected_cash_balances: dict[str, float] = {}
    if snapshots:
        # Use actual snapshot data
        for snap in snapshots[-30:]:  # Last 30 days
            projected_cash_balances[snap.snapshot_date.isoformat()] = float(snap.balance)
    else:
        # Simple projection based on outstanding invoices
        current_balance = 0.0
        projection_days = 30
        for i in range(projection_days):
            proj_date = today + timedelta(days=i)
            # Collect expected payments on this date
            expected_inflows = sum(
                float(inv.outstanding_amount) * 0.1  # Simplified:10% of outstanding per day
                for inv in invoices
                if inv.due_date <= proj_date
            )
            current_balance += expected_inflows
            projected_cash_balances[proj_date.isoformat()] = round(current_balance, 2)
    
    return TrialDashboardSummary(
        workspace_id=str(workspace_id),
        workspace_label=workspace.label,
        total_ar=total_ar,
        overdue_ar=overdue_ar,
        open_invoice_count=len(invoices),
        risky_invoice_count=risky_invoice_count,
        top_risky_customers=top_risky_customers,
        projected_cash_balances=projected_cash_balances,
        data_quality_score=workspace.data_quality_score,
        confidence_score=workspace.confidence_score,
    )


def get_trial_invoice_risk_queue(session: Session, workspace_id: UUID) -> list[dict[str, Any]]:
    """
    Get the invoice risk queue for a trial workspace.
    
    Args:
        session: Database session
        workspace_id: The trial workspace UUID
        
    Returns:
        List of invoice risk items
    """
    invoices = list(
        session.scalars(
            select(TrialInvoice)
            .options(selectinload(TrialInvoice.customer))
            .where(
                TrialInvoice.workspace_id == workspace_id,
                TrialInvoice.outstanding_amount > 0,
            )
            .order_by(TrialInvoice.due_date.asc())
        )
    )
    
    today = date.today()
    risk_queue = []
    
    for inv in invoices:
        overdue_days = max(0, (today - inv.due_date).days)
        risk_score = score_invoice(
            amount=float(inv.outstanding_amount),
            due_date=inv.due_date,
            customer_segment=inv.customer.segment if inv.customer else None,
            customer_industry=inv.customer.industry if inv.customer else None,
        )
        
        late_prob = risk_score.get("late_payment_probability", 0.5)
        if late_prob >= 0.8:
            risk_bucket = "high"
        elif late_prob >= 0.5:
            risk_bucket = "medium"
        else:
            risk_bucket = "low"
        
        risk_queue.append({
            "invoice_id": str(inv.id),
            "external_invoice_id": inv.external_invoice_id,
            "customer_name": inv.customer.name if inv.customer else "Unknown",
            "amount": float(inv.outstanding_amount),
            "due_date": inv.due_date.isoformat(),
            "overdue_days": overdue_days,
            "late_payment_probability": round(late_prob, 2),
            "risk_bucket": risk_bucket,
            "top_reason_codes": risk_score.get("risk_factors", [])[:3],
            "recommended_action": risk_score.get("recommended_action", "Monitor"),
        })
    
    return risk_queue