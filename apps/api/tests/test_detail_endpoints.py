def test_invoice_detail_endpoint(client, seed_data) -> None:
    response = client.get("/api/v1/invoices/INV-1002")
    assert response.status_code == 200
    payload = response.json()

    assert payload["invoice_id"] == "INV-1002"
    assert payload["customer_id"] == "CUST-002"
    assert payload["amount_paid"] == 20000.0
    assert payload["outstanding_amount"] == 9680.0
    assert payload["status"] == "partially_paid"
    assert payload["overdue_days"] == 4
    assert len(payload["payment_history"]) == 2
    assert payload["risk_bucket"] in {"low", "medium", "high"}
    assert payload["model_version"] == "v0.1.0-rules"
    assert payload["score_type"] == "rule-based"


def test_customer_detail_endpoint(client, seed_data) -> None:
    response = client.get("/api/v1/customers/CUST-001")
    assert response.status_code == 200
    payload = response.json()

    assert payload["customer_id"] == "CUST-001"
    assert payload["customer_name"] == "Northstar Dental Group"
    assert payload["open_exposure"] == 12720.0
    assert payload["open_invoice_count"] == 1
    assert payload["overdue_invoice_count"] == 1
    assert payload["average_days_overdue"] == 27.0
    assert len(payload["open_invoices"]) == 1
    assert payload["top_recommendation"]


def test_invoice_detail_not_found(client) -> None:
    response = client.get("/api/v1/invoices/INV-404")
    assert response.status_code == 404


def test_customer_detail_not_found(client) -> None:
    response = client.get("/api/v1/customers/CUST-404")
    assert response.status_code == 404
