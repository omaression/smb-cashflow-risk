from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DashboardSummaryResponse, TopRiskyCustomer
from app.services.portfolio import build_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryResponse:
    try:
        summary = build_dashboard_summary(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DashboardSummaryResponse(
        total_ar=float(summary.total_ar),
        overdue_ar=float(summary.overdue_ar),
        open_invoice_count=summary.open_invoice_count,
        risky_invoice_count=summary.risky_invoice_count,
        top_risky_customers=[TopRiskyCustomer(**c) for c in summary.top_risky_customers],
        projected_cash_balances=summary.projected_cash_balances,
    )
