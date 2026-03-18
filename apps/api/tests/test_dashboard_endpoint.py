def test_dashboard_summary_endpoint_uses_loaded_portfolio(client, seed_data) -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()

    assert payload["total_ar"] == 31410.0
    assert payload["overdue_ar"] == 31410.0
    assert payload["open_invoice_count"] == 3
    assert payload["risky_invoice_count"] == 2
    assert payload["top_risky_customers"][0] == "Northstar Dental Group"
    assert set(payload["projected_cash_balances"].keys()) == {"7", "14", "30"}