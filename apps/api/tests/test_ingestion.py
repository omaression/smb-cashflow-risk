from pathlib import Path

from app.ingestion import ingest_csv_file
from app.models import Customer, Invoice, Payment

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def test_ingest_sample_customer_file(db_session) -> None:
    result = ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    assert result.imported == 3
    assert result.rejected == 0
    assert db_session.query(Customer).count() == 3


def test_ingest_chain_customers_invoices_payments(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    result = ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)

    assert result.imported == 2
    invoice = db_session.query(Invoice).filter_by(external_invoice_id="INV-1002").one()
    assert float(invoice.outstanding_amount) == 9680.0
    assert invoice.status == "partially_paid"
    assert db_session.query(Payment).count() == 2


def test_invoice_import_rejects_missing_customer(db_session) -> None:
    result = ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    assert result.imported == 0
    assert result.rejected == 3
    assert "customer not found" in result.errors[0].message


def test_duplicate_ids_in_same_file_are_rejected(db_session) -> None:
    duplicate_csv = b"external_customer_id,name,industry,segment,country,payment_terms_days,credit_limit,is_active\nCUST-001,A,,,,30,1000,true\nCUST-001,B,,,,30,1000,true\n"
    result = ingest_csv_file("customers", duplicate_csv, db_session)
    assert result.imported == 1
    assert result.rejected == 1
    assert "duplicate external id" in result.errors[0].message
