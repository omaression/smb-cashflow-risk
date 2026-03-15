from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_summary() -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["open_invoice_count"] == 3
    assert "projected_cash_balances" in payload


def test_invoice_risk_list() -> None:
    response = client.get("/api/v1/invoices/risk")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["invoice_id"] == "INV-1001"
