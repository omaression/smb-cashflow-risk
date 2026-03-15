def test_healthcheck(client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_summary(client) -> None:
    client.post(
        "/api/v1/import/csv",
        data={"entity_type": "customers"},
        files={"file": ("sample_customers.csv", b"external_customer_id,name,industry,segment,country,payment_terms_days,credit_limit,is_active\nCUST-001,Northstar Dental Group,Healthcare,Mid-Market,US,30,75000,true\nCUST-002,Riverbend Industrial Supply,Manufacturing,SMB,US,45,120000,true\nCUST-003,Summit Office Interiors,Commercial Services,SMB,US,30,40000,true\n", "text/csv")},
    )
    client.post(
        "/api/v1/import/csv",
        data={"entity_type": "invoices"},
        files={"file": ("sample_invoices.csv", b"external_invoice_id,external_customer_id,invoice_date,due_date,currency,subtotal_amount,tax_amount,total_amount,outstanding_amount,status,payment_terms_days\nINV-1001,CUST-001,2026-01-10,2026-02-09,USD,12000,720,12720,12720,sent,30\nINV-1002,CUST-002,2026-01-18,2026-03-04,USD,28000,1680,29680,14680,partially_paid,45\nINV-1003,CUST-003,2026-02-02,2026-03-04,USD,8500,510,9010,9010,sent,30\n", "text/csv")},
    )
    client.post(
        "/api/v1/import/csv",
        data={"entity_type": "payments"},
        files={"file": ("sample_payments.csv", b"external_payment_id,external_invoice_id,external_customer_id,payment_date,amount,currency,payment_method,reference\nPAY-7001,INV-1002,CUST-002,2026-03-01,15000,USD,ACH,ACH-993201\nPAY-7002,INV-1002,CUST-002,2026-03-08,5000,USD,Wire,WIRE-11082\n", "text/csv")},
    )
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["open_invoice_count"] == 3
    assert payload["risky_invoice_count"] == 3
    assert payload["top_risky_customers"][0] == "Northstar Dental Group"
    assert "projected_cash_balances" in payload


def test_invoice_risk_list(client) -> None:
    response = client.get("/api/v1/invoices/risk")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["invoice_id"] == "INV-1001"


def test_cash_forecast(client) -> None:
    client.post(
        "/api/v1/import/csv",
        data={"entity_type": "cash_snapshots"},
        files={"file": ("sample_cash_snapshots.csv", b"snapshot_date,currency,opening_balance,cash_in,cash_out,closing_balance\n2026-03-01,USD,95000,18000,22000,91000\n2026-03-02,USD,91000,12000,15000,88000\n2026-03-03,USD,88000,24000,17000,95000\n", "text/csv")},
    )
    response = client.get("/api/v1/forecast/cash?horizon_days=14")
    assert response.status_code == 200
    payload = response.json()
    assert payload["horizon_days"] == 14
    assert payload["base_balance"] == 95000.0
    assert "projected_closing_balance" in payload
