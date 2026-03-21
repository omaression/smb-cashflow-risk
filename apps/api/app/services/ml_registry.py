from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.ml.registry import get_dataset_spec
from app.services.ml_artifacts import (
    get_comparison_artifact,
    get_latest_native_artifact,
    list_model_entries,
)
from app.services.ml_readiness import build_native_readiness_summary
from app.services.model_version import CURRENT_MODEL_VERSION

TRANSFER_SUMMARY = (
    "Keep the current runtime scorer rule-based. External benchmarks are useful as benchmark evidence and "
    "feature-discovery inputs, but they do not yet justify replacing runtime scoring."
)


def build_runtime_model_payload() -> dict[str, Any]:
    return {
        "version": CURRENT_MODEL_VERSION.version,
        "model_type": CURRENT_MODEL_VERSION.model_type,
        "target": CURRENT_MODEL_VERSION.target,
        "decision_threshold": CURRENT_MODEL_VERSION.decision_threshold,
        "evaluation_status": CURRENT_MODEL_VERSION.evaluation_status,
        "description": CURRENT_MODEL_VERSION.description,
        "features_used": CURRENT_MODEL_VERSION.features_used,
        "notes": CURRENT_MODEL_VERSION.notes,
        "limitations": [
            "Heuristic weights are not learned from historical optimization.",
            "Scores should not be interpreted as calibrated probabilities.",
            "This remains the most honest runtime default for the current demo dataset.",
        ],
    }


def build_native_readiness_payload() -> dict[str, Any]:
    native = get_latest_native_artifact()
    row_count = int(native.get("row_count", 0)) if native else 0
    positive_count = int(native.get("positive_count", 0)) if native else 0
    readiness = build_native_readiness_summary(row_count=row_count, positive_count=positive_count)
    payload = asdict(readiness)
    if native:
        payload.update(
            {
                "model_version": native.get("model_version"),
                "generated_at": native.get("generated_at"),
                "small_dataset_warning": native.get("small_dataset_warning"),
                "limitations": native.get("limitations", []),
            }
        )
    else:
        payload.update(
            {
                "model_version": None,
                "generated_at": None,
                "small_dataset_warning": "No project-native artifact is available yet.",
                "limitations": ["Generate a project-native workflow report before surfacing native readiness details."],
            }
        )
    return payload


def build_benchmark_payload() -> list[dict[str, Any]]:
    comparison = get_comparison_artifact()
    if comparison is None:
        return []

    benchmarks: list[dict[str, Any]] = []
    winner = comparison.get("winner")
    for dataset_key, metric_key in ((comparison.get("dataset_a"), "metric_a"), (comparison.get("dataset_b"), "metric_b")):
        if not dataset_key:
            continue
        spec = get_dataset_spec(dataset_key)
        benchmarks.append(
            {
                "dataset_key": dataset_key,
                "name": spec.name,
                "description": spec.description,
                "target": spec.target_column,
                "headline_metric": comparison.get(metric_key),
                "winner": winner == dataset_key,
                "caveats": [
                    "Benchmark results are for external datasets, not direct runtime validation.",
                    "Use these runs to compare modeling behavior and feature ideas, not to justify runtime model transfer.",
                ],
            }
        )
    return benchmarks


def build_ml_overview_payload() -> dict[str, Any]:
    return {
        "runtime_model": build_runtime_model_payload(),
        "native_pipeline": build_native_readiness_payload(),
        "external_benchmarks": build_benchmark_payload(),
        "transfer_recommendation": {
            "keep_runtime_rule_based": True,
            "summary": TRANSFER_SUMMARY,
        },
    }


def build_model_catalog_payload() -> list[dict[str, Any]]:
    return [asdict(entry) for entry in list_model_entries()]


def get_model_detail_payload(model_version: str) -> dict[str, Any] | None:
    if model_version == CURRENT_MODEL_VERSION.version:
        return {
            **build_runtime_model_payload(),
            "title": "Runtime scoring baseline",
            "approved_for_runtime": True,
            "dataset_key": "runtime",
            "summary": "Current rule-based scoring baseline used throughout the application.",
        }

    for entry in list_model_entries():
        if entry.model_version == model_version:
            payload = asdict(entry)
            if entry.dataset_key and entry.dataset_key not in {"runtime", None}:
                try:
                    spec = get_dataset_spec(entry.dataset_key)
                    payload["source_hint"] = spec.source_hint
                    payload["target"] = spec.target_column
                except KeyError:
                    pass
            return payload
    return None
