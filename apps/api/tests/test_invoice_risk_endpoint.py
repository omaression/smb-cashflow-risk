def test_invoice_risk_endpoint_returns_ranked_results(client, seed_data) -> None:
    response = client.get("/api/v1/invoices/risk")
    assert response.status_code == 200
    payload = response.json()

    assert len(payload) == 3
    assert payload[0]["invoice_id"] == "INV-1001"
    assert payload[1]["invoice_id"] == "INV-1002"
    assert payload[0]["risk_bucket"] == "high"
    assert payload[1]["risk_bucket"] == "medium"
    assert payload[2]["risk_bucket"] == "low"