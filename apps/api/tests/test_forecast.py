from app.ingestion import ingest_csv_file


def _load_seed_data(db_session) -> None:
    from pathlib import Path

    data_dir = Path(__file__).resolve().parents[3] / "data" / "raw"
    ingest_csv_file("customers", (data_dir / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (data_dir / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (data_dir / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (data_dir / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_cash_forecast_base_7_day(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/forecast/cash?horizon_days=7&scenario=base")
    assert response.status_code == 200
    payload = response.json()

    assert payload["horizon_days"] == 7
    assert payload["scenario"] == "base"
    assert payload["currency"] == "USD"
    assert payload["starting_balance"] == 95000.0
    assert len(payload["series"]) == 1
    point = payload["series"][0]
    assert point["forecast_date"] == "2026-03-10"
    assert point["expected_inflows"] == 17353.5
    assert point["expected_outflows"] == 119000.0
    assert point["projected_balance"] == -6646.5


def test_cash_forecast_downside_30_day(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/forecast/cash?horizon_days=30&scenario=downside")
    assert response.status_code == 200
    payload = response.json()

    point = payload["series"][0]
    assert point["forecast_date"] == "2026-04-02"
    assert point["expected_inflows"] == 16042.5
    assert point["expected_outflows"] == 561000.0
    assert point["projected_balance"] == -449957.5


def test_cash_forecast_rejects_unsupported_horizon(client, db_session) -> None:
    _load_seed_data(db_session)

    response = client.get("/api/v1/forecast/cash?horizon_days=10&scenario=base")
    assert response.status_code == 400
    assert "unsupported horizon_days" in response.json()["detail"]
