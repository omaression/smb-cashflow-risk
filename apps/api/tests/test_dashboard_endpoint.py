import httpx
import pytest

from app.database import get_db
from app.main import app


@pytest.mark.anyio
async def test_dashboard_summary_endpoint_uses_loaded_portfolio(seed_data) -> None:
    def override_get_db():
        yield seed_data

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/dashboard/summary")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()

    assert payload["total_ar"] == 31410.0
    assert payload["overdue_ar"] == 31410.0
    assert payload["open_invoice_count"] == 3
    assert payload["risky_invoice_count"] == 2
    assert payload["top_risky_customers"][0] == {"id": "CUST-001", "name": "Northstar Dental Group"}
    assert set(payload["projected_cash_balances"].keys()) == {"7", "14", "30"}
    assert payload["runtime_model_version"] == "v0.1.0-rules"
    assert payload["ml_status_badge"] == "rules-only"


@pytest.mark.anyio
async def test_dashboard_summary_endpoint_succeeds_without_cash_snapshots(
    seed_data_without_cash_snapshots,
) -> None:
    def override_get_db():
        yield seed_data_without_cash_snapshots

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/dashboard/summary")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()

    assert payload["total_ar"] == 31410.0
    assert payload["overdue_ar"] == 31410.0
    assert payload["open_invoice_count"] == 3
    assert payload["risky_invoice_count"] == 2
    assert payload["projected_cash_balances"] == {}
