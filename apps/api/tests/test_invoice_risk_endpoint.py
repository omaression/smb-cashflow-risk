from pathlib import Path

from app.ingestion import ingest_csv_file

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _load_seed_data(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)


def test_invoice_risk_endpoint_returns_ranked_results(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/invoices/risk")
    assert response.status_code == 200
    payload = response.json()

    assert len(payload) == 3
    assert payload[0]["invoice_id"] == "INV-1001"
    assert payload[1]["invoice_id"] == "INV-1002"
    assert payload[0]["risk_bucket"] == "high"
    assert payload[1]["risk_bucket"] == "medium"
    assert payload[2]["risk_bucket"] == "low"
