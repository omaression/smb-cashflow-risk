from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CashForecastResponse
from app.services.dashboard import project_cash_balance

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/cash", response_model=CashForecastResponse)
def get_cash_forecast(
    horizon_days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
) -> CashForecastResponse:
    return CashForecastResponse(**project_cash_balance(db, horizon_days=horizon_days))
