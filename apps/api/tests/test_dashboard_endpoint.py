from pathlib import Path

from app.ingestion import ingest_csv_file

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _load_seed_data(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_dashboard_summary_endpoint_uses_loaded_portfolio(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()

    assert payload["total_ar"] == 31410.0
    assert payload["overdue_ar"] == 31410.0
    assert payload["open_invoice_count"] == 3
    assert payload["risky_invoice_count"] == 2
    assert payload["top_risky_customers"][0] == "Northstar Dental Group"
    assert set(payload["projected_cash_balances"].keys()) == {"7", "14", "30"}
