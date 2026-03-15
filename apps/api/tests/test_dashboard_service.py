from datetime import date
from pathlib import Path

from app.ingestion import ingest_csv_file
from app.services.dashboard import build_dashboard_summary, project_cash_balance

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _seed_all(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_build_dashboard_summary(db_session) -> None:
    _seed_all(db_session)
    summary = build_dashboard_summary(db_session, today=date(2026, 3, 15))

    assert summary["open_invoice_count"] == 3
    assert summary["risky_invoice_count"] == 3
    assert summary["total_ar"] == 31410.0
    assert summary["overdue_ar"] == 31410.0
    assert summary["top_risky_customers"][0] == "Northstar Dental Group"


def test_project_cash_balance(db_session) -> None:
    _seed_all(db_session)
    forecast = project_cash_balance(db_session, horizon_days=14, today=date(2026, 3, 15))

    assert forecast["horizon_days"] == 14
    assert forecast["base_balance"] == 95000.0
    assert forecast["expected_inflows"] > 0
    assert forecast["projected_closing_balance"] > 0
