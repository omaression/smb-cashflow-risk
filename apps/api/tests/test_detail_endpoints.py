from app.ingestion import ingest_csv_file


def _load_seed_data(db_session) -> None:
    from pathlib import Path

    data_dir = Path(__file__).resolve().parents[3] / "data" / "raw"
    ingest_csv_file("customers", (data_dir / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (data_dir / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (data_dir / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (data_dir / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_invoice_detail_endpoint(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/invoices/INV-1002")
    assert response.status_code == 200
    payload = response.json()

    assert payload["invoice_id"] == "INV-1002"
    assert payload["customer_id"] == "CUST-002"
    assert payload["amount_paid"] == 20000.0
    assert payload["outstanding_amount"] == 9680.0
    assert payload["status"] == "partially_paid"
    assert len(payload["payment_history"]) == 2
    assert payload["risk_bucket"] in {"low", "medium", "high"}


def test_customer_detail_endpoint(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/customers/CUST-001")
    assert response.status_code == 200
    payload = response.json()

    assert payload["customer_id"] == "CUST-001"
    assert payload["customer_name"] == "Northstar Dental Group"
    assert payload["open_exposure"] == 12720.0
    assert payload["open_invoice_count"] == 1
    assert payload["overdue_invoice_count"] == 1
    assert len(payload["open_invoices"]) == 1
    assert payload["top_recommendation"]


def test_invoice_detail_not_found(client) -> None:
    response = client.get("/api/v1/invoices/INV-404")
    assert response.status_code == 404


def test_customer_detail_not_found(client) -> None:
    response = client.get("/api/v1/customers/CUST-404")
    assert response.status_code == 404
