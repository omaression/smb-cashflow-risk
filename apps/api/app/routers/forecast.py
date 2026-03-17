from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CashForecastPoint, CashForecastResponse
from app.services.forecast import build_cash_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/cash", response_model=CashForecastResponse)
def get_cash_forecast(
    horizon_days: int = Query(default=7),
    scenario: str = Query(default="base"),
    db: Session = Depends(get_db),
) -> CashForecastResponse:
    try:
        result = build_cash_forecast(session=db, horizon_days=horizon_days, scenario=scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CashForecastResponse(
        horizon_days=result.horizon_days,
        scenario=result.scenario,
        currency=result.currency,
        starting_balance=float(result.starting_balance),
        series=[
            CashForecastPoint(
                forecast_date=point.forecast_date,
                projected_balance=float(point.projected_balance),
                expected_inflows=float(point.expected_inflows),
                expected_outflows=float(point.expected_outflows),
            )
            for point in result.series
        ],
    )
