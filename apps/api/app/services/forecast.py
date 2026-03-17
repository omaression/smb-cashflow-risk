from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailyCashSnapshot, Invoice

OPEN_INVOICE_STATUSES = {"sent", "partially_paid"}
BASE_COLLECTION_RATE = Decimal("0.70")
DOWNSIDE_COLLECTION_RATE = Decimal("0.45")
MINIMUM_COLLECTION_RATE = Decimal("0.20")
OVERDUE_COLLECTION_BOOST = Decimal("0.15")
SEVEN_DAY_COLLECTION_SHARE = Decimal("0.50")
FOURTEEN_DAY_COLLECTION_SHARE = Decimal("0.75")
THIRTY_DAY_COLLECTION_SHARE = Decimal("1.00")
DEFAULT_DAILY_OUTFLOW = Decimal("5000.00")
DOWNSIDE_OUTFLOW_MULTIPLIER = Decimal("1.10")
SUPPORTED_HORIZONS = {7, 14, 30}
SUPPORTED_SCENARIOS = {"base", "downside"}


@dataclass(frozen=True)
class ForecastPoint:
    forecast_date: date
    projected_balance: Decimal
    expected_inflows: Decimal
    expected_outflows: Decimal


@dataclass(frozen=True)
class ForecastResult:
    horizon_days: int
    scenario: str
    starting_balance: Decimal
    currency: str
    series: list[ForecastPoint]


def _to_decimal(value: Decimal | int | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _latest_snapshot(session: Session) -> DailyCashSnapshot:
    snapshot = session.scalar(
        select(DailyCashSnapshot).order_by(DailyCashSnapshot.snapshot_date.desc()).limit(1)
    )
    if snapshot is None:
        raise ValueError("cash forecast unavailable: no cash snapshots loaded")
    return snapshot


def _open_invoices(session: Session) -> list[Invoice]:
    return list(
        session.scalars(
            select(Invoice)
            .where(Invoice.status.in_(OPEN_INVOICE_STATUSES), Invoice.outstanding_amount > 0)
            .order_by(Invoice.due_date.asc(), Invoice.external_invoice_id.asc())
        )
    )


def _collection_rate(invoice: Invoice, as_of: date, scenario: str) -> Decimal:
    rate = BASE_COLLECTION_RATE if scenario == "base" else DOWNSIDE_COLLECTION_RATE
    if invoice.due_date < as_of:
        rate += OVERDUE_COLLECTION_BOOST
    return min(Decimal("1.00"), max(MINIMUM_COLLECTION_RATE, rate))


def _collection_share(invoice: Invoice, as_of: date, horizon_days: int) -> Decimal:
    if invoice.due_date < as_of:
        return Decimal("1.00")

    days_until_due = (invoice.due_date - as_of).days
    if days_until_due <= 7:
        return SEVEN_DAY_COLLECTION_SHARE if horizon_days == 7 else Decimal("1.00")
    if days_until_due <= 14:
        return Decimal("0.00") if horizon_days == 7 else (FOURTEEN_DAY_COLLECTION_SHARE if horizon_days == 14 else Decimal("1.00"))
    if days_until_due <= 30:
        return Decimal("0.00") if horizon_days in {7, 14} else THIRTY_DAY_COLLECTION_SHARE
    return Decimal("0.00")


def _expected_inflows(invoices: list[Invoice], as_of: date, horizon_days: int, scenario: str) -> Decimal:
    total = Decimal("0.00")
    for invoice in invoices:
        collection_rate = _collection_rate(invoice, as_of=as_of, scenario=scenario)
        horizon_share = _collection_share(invoice, as_of=as_of, horizon_days=horizon_days)
        total += _to_decimal(invoice.outstanding_amount) * collection_rate * horizon_share
    return total.quantize(Decimal("0.01"))


def _expected_outflows(snapshot: DailyCashSnapshot, horizon_days: int, scenario: str) -> Decimal:
    baseline_daily_outflow = _to_decimal(snapshot.cash_out) if snapshot.cash_out > 0 else DEFAULT_DAILY_OUTFLOW
    daily_outflow = baseline_daily_outflow
    if scenario == "downside":
        daily_outflow *= DOWNSIDE_OUTFLOW_MULTIPLIER
    return (daily_outflow * horizon_days).quantize(Decimal("0.01"))


def build_cash_forecast(session: Session, horizon_days: int, scenario: str) -> ForecastResult:
    if horizon_days not in SUPPORTED_HORIZONS:
        raise ValueError(f"unsupported horizon_days: {horizon_days}")
    if scenario not in SUPPORTED_SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")

    snapshot = _latest_snapshot(session)
    invoices = _open_invoices(session)
    as_of = snapshot.snapshot_date
    starting_balance = _to_decimal(snapshot.closing_balance)
    expected_inflows = _expected_inflows(invoices, as_of=as_of, horizon_days=horizon_days, scenario=scenario)
    expected_outflows = _expected_outflows(snapshot, horizon_days=horizon_days, scenario=scenario)
    ending_balance = (starting_balance + expected_inflows - expected_outflows).quantize(Decimal("0.01"))

    point = ForecastPoint(
        forecast_date=as_of + timedelta(days=horizon_days),
        projected_balance=ending_balance,
        expected_inflows=expected_inflows,
        expected_outflows=expected_outflows,
    )
    return ForecastResult(
        horizon_days=horizon_days,
        scenario=scenario,
        starting_balance=starting_balance.quantize(Decimal("0.01")),
        currency=snapshot.currency,
        series=[point],
    )
