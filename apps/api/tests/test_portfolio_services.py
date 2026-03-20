from app.services.portfolio import build_dashboard_summary, rank_open_invoices, resolve_portfolio_as_of


def test_resolve_portfolio_as_of_uses_latest_observed_portfolio_date(seed_data) -> None:
    assert str(resolve_portfolio_as_of(seed_data)) == "2026-03-08"


def test_rank_open_invoices_orders_by_priority(seed_data) -> None:
    ranked = rank_open_invoices(seed_data)

    assert [item.invoice_id for item in ranked] == ["INV-1001", "INV-1002", "INV-1003"]
    assert ranked[0].risk_bucket == "high"
    assert ranked[1].customer_name == "Riverbend Industrial Supply"
    assert ranked[0].priority_score > ranked[1].priority_score > ranked[2].priority_score


def test_build_dashboard_summary_uses_ranked_portfolio(seed_data) -> None:
    summary = build_dashboard_summary(seed_data)

    assert float(summary.total_ar) == 31410.0
    assert float(summary.overdue_ar) == 31410.0
    assert summary.open_invoice_count == 3
    assert summary.risky_invoice_count == 2
    assert summary.top_risky_customers == [
        {"id": "CUST-001", "name": "Northstar Dental Group"},
        {"id": "CUST-002", "name": "Riverbend Industrial Supply"},
    ]
    assert set(summary.projected_cash_balances.keys()) == {"7", "14", "30"}