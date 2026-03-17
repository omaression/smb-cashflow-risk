from pathlib import Path

from app.ingestion import ingest_csv_file
from app.services.portfolio import build_dashboard_summary, rank_open_invoices

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _load_seed_data(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_rank_open_invoices_orders_by_priority(db_session) -> None:
    _load_seed_data(db_session)

    ranked = rank_open_invoices(db_session)

    assert [item.invoice_id for item in ranked] == ["INV-1001", "INV-1002", "INV-1003"]
    assert ranked[0].risk_bucket == "high"
    assert ranked[1].customer_name == "Riverbend Industrial Supply"
    assert ranked[0].priority_score > ranked[1].priority_score > ranked[2].priority_score


def test_build_dashboard_summary_uses_ranked_portfolio(db_session) -> None:
    _load_seed_data(db_session)

    summary = build_dashboard_summary(db_session)

    assert float(summary.total_ar) == 31410.0
    assert float(summary.overdue_ar) == 31410.0
    assert summary.open_invoice_count == 3
    assert summary.risky_invoice_count == 2
    assert summary.top_risky_customers == ["Northstar Dental Group", "Riverbend Industrial Supply"]
    assert set(summary.projected_cash_balances.keys()) == {"7", "14", "30"}
