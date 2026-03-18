from pathlib import Path

from app.ingestion import ingest_csv_file
from app.services.features import build_invoice_feature_rows
from app.services.scoring import build_and_export_features, evaluate_baseline

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def _load_seed_data(db_session) -> None:
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)


def test_evaluate_baseline_scores_expected_invoice_order(db_session) -> None:
    _load_seed_data(db_session)
    rows = build_invoice_feature_rows(db_session)

    scored_rows, evaluation = evaluate_baseline(rows)
    by_invoice = {row.invoice_id: row for row in scored_rows}

    assert by_invoice["INV-1001"].risk_bucket == "high"
    assert by_invoice["INV-1002"].risk_bucket == "medium"
    assert by_invoice["INV-1003"].risk_bucket == "low"
    assert evaluation.row_count == 3
    assert evaluation.positive_labels == 1
    assert evaluation.predicted_positive == 2
    assert evaluation.recall == 1.0


def test_build_and_export_features_writes_csv(db_session, tmp_path) -> None:
    _load_seed_data(db_session)

    output_path = tmp_path / "invoice_features.csv"
    written_path = build_and_export_features(db_session, output_path)

    assert written_path == output_path
    text = output_path.read_text(encoding="utf-8")
    assert "invoice_id,customer_id,customer_name" in text
    assert "INV-1001" in text
