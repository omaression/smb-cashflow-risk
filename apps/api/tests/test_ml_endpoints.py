def test_ml_overview_endpoint_returns_runtime_and_native_status(client) -> None:
    response = client.get("/api/v1/ml/overview")
    assert response.status_code == 200
    payload = response.json()

    assert payload["runtime_model"]["version"] == "v0.1.0-rules"
    assert payload["runtime_model"]["model_type"] == "rule-based"
    assert payload["native_pipeline"]["status"] == "deferred"
    assert payload["transfer_recommendation"]["keep_runtime_rule_based"] is True
    assert len(payload["external_benchmarks"]) >= 1


def test_ml_models_endpoint_lists_runtime_entry(client) -> None:
    response = client.get("/api/v1/ml/models")
    assert response.status_code == 200
    payload = response.json()

    runtime_entry = next(item for item in payload if item["model_version"] == "v0.1.0-rules")
    assert runtime_entry["approved_for_runtime"] is True
    assert runtime_entry["dataset_key"] == "runtime"


def test_ml_model_detail_endpoint_returns_runtime_card(client) -> None:
    response = client.get("/api/v1/ml/models/v0.1.0-rules")
    assert response.status_code == 200
    payload = response.json()

    assert payload["approved_for_runtime"] is True
    assert payload["title"] == "Runtime scoring baseline"
    assert payload["summary"]


def test_native_readiness_endpoint_exposes_thresholds(client) -> None:
    response = client.get("/api/v1/ml/native-readiness")
    assert response.status_code == 200
    payload = response.json()

    assert payload["min_rows_required"] == 200
    assert payload["min_positive_rows_required"] == 25
    assert payload["next_unlock_condition"]


def test_unknown_model_returns_404(client) -> None:
    response = client.get("/api/v1/ml/models/does-not-exist")
    assert response.status_code == 404
