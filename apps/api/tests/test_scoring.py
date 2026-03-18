from app.services.features import build_invoice_feature_rows
from app.services.scoring import build_and_export_features, evaluate_baseline, export_feature_rows_to_csv
import pytest


def test_evaluate_baseline_scores_expected_invoice_order(seed_data) -> None:
    rows = build_invoice_feature_rows(seed_data)

    scored_rows, evaluation = evaluate_baseline(rows)
    by_invoice = {row.invoice_id: row for row in scored_rows}

    assert by_invoice["INV-1001"].risk_bucket == "high"
    assert by_invoice["INV-1002"].risk_bucket == "medium"
    assert by_invoice["INV-1003"].risk_bucket == "low"
    assert evaluation.row_count == 3
    assert evaluation.positive_labels == 1
    assert evaluation.predicted_positive == 2
    assert evaluation.recall == 1.0


def test_export_feature_rows_to_csv_writes_header_for_empty_input(tmp_path) -> None:
    output_path = tmp_path / "empty_invoice_features.csv"

    written_path = export_feature_rows_to_csv([], output_path)

    assert written_path == output_path
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("invoice_id,customer_id,customer_name")
    assert len(lines) == 1


def test_build_and_export_features_writes_csv(seed_data, tmp_path) -> None:
    output_path = tmp_path / "invoice_features.csv"
    written_path = build_and_export_features(seed_data, output_path)

    assert written_path == output_path
    text = output_path.read_text(encoding="utf-8")
    assert "invoice_id,customer_id,customer_name" in text
    assert "INV-1001" in text


def test_build_and_export_features_raises_on_empty_db(db_session) -> None:
    """Verify ValueError when no invoice features are available."""
    import pytest
    with pytest.raises(ValueError, match="no invoice features available"):
        build_and_export_features(db_session, "/tmp/output.csv")