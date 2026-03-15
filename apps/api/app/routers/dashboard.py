from fastapi import APIRouter

from app.schemas import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary() -> DashboardSummaryResponse:
    return DashboardSummaryResponse(
        total_ar=51410.0,
        overdue_ar=27400.0,
        open_invoice_count=3,
        risky_invoice_count=2,
        top_risky_customers=[
            "Riverbend Industrial Supply",
            "Northstar Dental Group",
        ],
        projected_cash_balances={"7": 90500.0, "14": 97800.0, "30": 110400.0},
    )
