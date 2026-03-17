from pathlib import Path

from app.ingestion import ingest_csv_file
from app.services.features import build_invoice_feature_rows

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _load_seed_data(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_build_invoice_feature_rows_returns_expected_derived_fields(db_session) -> None:
    _load_seed_data(db_session)

    rows = build_invoice_feature_rows(db_session)
    assert len(rows) == 3

    by_invoice = {row.invoice_id: row for row in rows}

    inv_1001 = by_invoice["INV-1001"]
    assert inv_1001.payment_terms_days == 30
    assert inv_1001.invoice_age_days == 57
    assert inv_1001.overdue_days == 27
    assert inv_1001.customer_open_exposure == 12720.00
    assert inv_1001.payment_count == 0
    assert inv_1001.paid_ratio == 0.0
    assert inv_1001.is_open is True
    assert inv_1001.is_late_15 == 1

    inv_1002 = by_invoice["INV-1002"]
    assert inv_1002.payment_terms_days == 45
    assert inv_1002.overdue_days == 4
    assert inv_1002.payment_count == 2
    assert inv_1002.paid_amount == 20000.00
    assert inv_1002.paid_ratio == 0.67
    assert inv_1002.is_late_15 == 0

    inv_1003 = by_invoice["INV-1003"]
    assert inv_1003.customer_name == "Summit Office Interiors"
    assert inv_1003.customer_invoice_count == 1
    assert inv_1003.days_until_due == -4
    assert inv_1003.is_late_15 == 0
