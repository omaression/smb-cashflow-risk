"""
Trial workspace summary building logic.

Phase 1: Placeholder for future implementation.
Phase 2: Will aggregate trial workspace data into dashboard summaries.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.trial_workspace import TrialWorkspace


@dataclass(frozen=True)
class TrialDashboardSummary:
    """Summary data for a trial workspace dashboard."""
    
    workspace_id: UUID
    workspace_label: str
    data_quality_score: float | None
    confidence_score: float | None
    total_ar: Decimal
    overdue_ar: Decimal
    open_invoice_count: int
    risky_invoice_count: int
    top_risky_customers: list[dict[str, str]]
    projected_cash_balances: dict[str, float]


def build_trial_summary(workspace: TrialWorkspace, db: Session) -> TrialDashboardSummary:
    """
    Build a dashboard summary for a trial workspace.
    
    Phase 1: Returns stub implementation.
    Phase 2: Will aggregate actual trial workspace data.
    
    Args:
        workspace: The trial workspace to summarize
        db: Database session
        
    Returns:
        TrialDashboardSummary with workspace metadata and financial metrics
    """
    # TODO: Phase 2 implementation
    # For Phase 1, this is a placeholder that should not be called directly.
    # The trial_dashboard router will call the regular build_dashboard_summary
    # and add workspace metadata on top.
    raise NotImplementedError("Trial summary building is a Phase 2 feature. Use portfolio.build_dashboard_summary for Phase 1 stub.")