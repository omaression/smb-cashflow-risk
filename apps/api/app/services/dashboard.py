from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Customer, DailyCashSnapshot, Invoice


def _overdue_days(today: date, due_date: date) -> int:
    return max((today - due_date).days, 0)


def _resolve_today(session: Session, today: date | None = None) -> date:
    if today is not None:
        return today

    latest_snapshot_date = session.scalar(select(func.max(DailyCashSnapshot.snapshot_date)))
    if latest_snapshot_date is not None:
        return latest_snapshot_date

    return date.today()


def build_dashboard_summary(session: Session, today: date | None = None) -> dict:
    today = _resolve_today(session, today)

    open_statuses = ("sent", "partially_paid")

    total_ar = session.scalar(
        select(func.coalesce(func.sum(Invoice.outstanding_amount), 0)).where(Invoice.status.in_(open_statuses))
    ) or Decimal("0")

    overdue_ar = session.scalar(
        select(func.coalesce(func.sum(Invoice.outstanding_amount), 0)).where(
            Invoice.status.in_(open_statuses),
            Invoice.due_date < today,
        )
    ) or Decimal("0")

    open_invoice_count = session.scalar(
        select(func.count()).select_from(Invoice).where(Invoice.status.in_(open_statuses))
    ) or 0

    risky_invoice_count = session.scalar(
        select(func.count()).select_from(Invoice).where(
            Invoice.status.in_(open_statuses),
            Invoice.due_date < today,
        )
    ) or 0

    customer_rows = session.execute(
        select(
            Customer.name,
            func.coalesce(func.sum(Invoice.outstanding_amount), 0).label("exposure"),
        )
        .join(Invoice, Invoice.customer_id == Customer.id)
        .where(Invoice.status.in_(open_statuses))
        .group_by(Customer.name)
        .order_by(func.sum(Invoice.outstanding_amount).desc())
        .limit(5)
    ).all()

    top_risky_customers = [row.name for row in customer_rows]

    projected_cash_balances = {
        str(horizon): project_cash_balance(session, horizon_days=horizon, today=today)["projected_closing_balance"]
        for horizon in (7, 14, 30)
    }

    return {
        "total_ar": float(total_ar),
        "overdue_ar": float(overdue_ar),
        "open_invoice_count": int(open_invoice_count),
        "risky_invoice_count": int(risky_invoice_count),
        "top_risky_customers": top_risky_customers,
        "projected_cash_balances": projected_cash_balances,
    }


def project_cash_balance(session: Session, horizon_days: int, today: date | None = None) -> dict:
    snapshot = session.execute(
        select(DailyCashSnapshot)
        .order_by(DailyCashSnapshot.snapshot_date.desc())
        .limit(1)
    ).scalar_one_or_none()

    today = _resolve_today(session, today)

    base_balance = snapshot.closing_balance if snapshot else Decimal("0")

    horizon_end = today + timedelta(days=horizon_days)
    open_invoices = session.scalars(
        select(Invoice).where(
            Invoice.status.in_(("sent", "partially_paid")),
            Invoice.outstanding_amount > 0,
            Invoice.due_date <= horizon_end,
        )
    ).all()

    expected_inflows = Decimal("0")
    downside_inflows = Decimal("0")

    for invoice in open_invoices:
        days_overdue = _overdue_days(today, invoice.due_date)
        if days_overdue >= 30:
            probability = Decimal("0.35")
        elif days_overdue > 0:
            probability = Decimal("0.60")
        else:
            probability = Decimal("0.85")

        expected_inflows += invoice.outstanding_amount * probability
        downside_inflows += invoice.outstanding_amount * min(probability, Decimal("0.50"))

    recent_cash_out_total = session.scalar(
        select(func.coalesce(func.sum(DailyCashSnapshot.cash_out), 0)).where(
            DailyCashSnapshot.snapshot_date >= today - timedelta(days=30),
            DailyCashSnapshot.snapshot_date <= today,
        )
    ) or Decimal("0")
    average_daily_outflow = recent_cash_out_total / Decimal("30") if recent_cash_out_total else Decimal("0")
    projected_outflows = average_daily_outflow * Decimal(str(horizon_days))

    return {
        "as_of_date": today.isoformat(),
        "horizon_days": horizon_days,
        "base_balance": float(base_balance),
        "expected_inflows": float(expected_inflows),
        "downside_inflows": float(downside_inflows),
        "projected_outflows": float(projected_outflows),
        "projected_closing_balance": float(base_balance + expected_inflows - projected_outflows),
        "downside_closing_balance": float(base_balance + downside_inflows - projected_outflows),
    }
