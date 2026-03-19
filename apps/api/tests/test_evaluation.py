from app.services.evaluation import MIN_SAMPLES_FOR_MEANINGFUL_METRICS, evaluate_model, generate_evaluation_report, save_evaluation_artifact, score_and_evaluate_split, split_features
from app.services.features import build_invoice_feature_rows
from app.services.model_version import CURRENT_MODEL_VERSION
from app.services.scoring import BaselineScoreRow
import json


def test_split_features_is_deterministic(seed_data) -> None:
    rows = build_invoice_feature_rows(seed_data)
    first = split_features(rows)
    second = split_features(rows)

    assert [row.invoice_id for row in first.train] == [row.invoice_id for row in second.train]
    assert [row.invoice_id for row in first.validation] == [row.invoice_id for row in second.validation]
    assert [row.invoice_id for row in first.test] == [row.invoice_id for row in second.test]


def test_split_features_flags_small_dataset(seed_data) -> None:
    rows = build_invoice_feature_rows(seed_data)
    split = split_features(rows)

    assert split.is_small_dataset is True
    assert split.warning is not None
    assert split.train == rows
    assert split.validation == rows
    assert split.test == rows


def test_evaluate_model_returns_warning_for_small_dataset() -> None:
    scored_rows = [
        BaselineScoreRow("i1", "c1", 0.9, 1, 1, "high", ["x"]),
        BaselineScoreRow("i2", "c1", 0.4, 0, 0, "low", ["y"]),
        BaselineScoreRow("i3", "c2", 0.7, 1, 0, "medium", ["z"]),
    ]
    result = evaluate_model(scored_rows, "test")

    assert result.metrics_status == "demonstration_only"
    assert result.warning is not None
    assert result.accuracy is None
    assert result.confusion_matrix == {"tp": 1, "fp": 1, "tn": 1, "fn": 0}


def test_evaluate_model_computes_metrics_above_threshold() -> None:
    scored_rows = [
        BaselineScoreRow(f"i{i}", "c", 0.9, 1 if i % 2 == 0 else 0, 1 if i in {0, 2, 4, 6, 8} else 0, "high", [])
        for i in range(MIN_SAMPLES_FOR_MEANINGFUL_METRICS)
    ]
    result = evaluate_model(scored_rows, "test")

    assert result.metrics_status == "computed"
    assert result.accuracy is not None
    assert result.precision is not None
    assert result.recall is not None


def test_save_evaluation_artifact_writes_valid_json(seed_data, tmp_path) -> None:
    rows = build_invoice_feature_rows(seed_data)
    split = split_features(rows)
    _, evaluation = score_and_evaluate_split(split.test, "test")

    path = save_evaluation_artifact(
        tmp_path,
        CURRENT_MODEL_VERSION,
        {"test": evaluation},
        small_dataset_warning=split.warning,
        limitations=["demo limitation"],
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["model_version"] == CURRENT_MODEL_VERSION.version
    assert payload["small_dataset_warning"] == split.warning
    assert payload["splits"]["test"]["metrics_status"] == "demonstration_only"


def test_generate_evaluation_report_contains_expected_sections(seed_data, tmp_path) -> None:
    rows = build_invoice_feature_rows(seed_data)
    split = split_features(rows)
    _, evaluation = score_and_evaluate_split(split.test, "test")

    path = generate_evaluation_report(
        tmp_path,
        CURRENT_MODEL_VERSION,
        {"test": evaluation},
        small_dataset_warning=split.warning,
        limitations=["demo limitation"],
    )

    text = path.read_text(encoding="utf-8")
    assert "# Baseline Model Evaluation Report" in text
    assert "## ⚠️ Limitations First" in text
    assert "## Model Identity" in text
    assert "## Metrics" in text


def test_current_model_version_has_required_fields() -> None:
    assert CURRENT_MODEL_VERSION.version.startswith("v")
    assert CURRENT_MODEL_VERSION.model_type == "rule-based"
    assert CURRENT_MODEL_VERSION.target == "is_late_15"
    assert CURRENT_MODEL_VERSION.features_used
