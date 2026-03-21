from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ARTIFACTS_ROOT = Path(__file__).resolve().parents[4] / "artifacts"
EVALUATIONS_DIR = ARTIFACTS_ROOT / "evaluations"
ML_ROOT = ARTIFACTS_ROOT / "ml"
PROJECT_NATIVE_DIR = ML_ROOT / "project_native"
COMPARISON_PATH = ML_ROOT / "comparisons" / "comparison.json"


@dataclass(frozen=True)
class ArtifactModelEntry:
    model_version: str
    model_type: str
    title: str
    evaluation_status: str
    generated_at: str | None
    summary: str
    limitations: list[str]
    metrics: dict[str, Any] | None
    artifact_path: str
    dataset_key: str | None = None
    approved_for_runtime: bool = False


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.name == ".gitkeep":
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _latest_json(directory: Path) -> Path | None:
    candidates = [path for path in directory.glob("*.json") if path.name != ".gitkeep"]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def get_latest_runtime_evaluation() -> dict[str, Any] | None:
    latest = _latest_json(EVALUATIONS_DIR)
    if latest is None:
        return None
    return _load_json(latest)


def get_latest_native_artifact() -> dict[str, Any] | None:
    latest = _latest_json(PROJECT_NATIVE_DIR)
    if latest is None:
        return None
    return _load_json(latest)


def get_comparison_artifact() -> dict[str, Any] | None:
    return _load_json(COMPARISON_PATH)


def _humanize_dataset_key(dataset_key: str) -> str:
    mapping = {
        "ibm": "IBM benchmark",
        "skywalker": "Skywalker benchmark",
        "native": "Project-native workflow demo",
    }
    return mapping.get(dataset_key, dataset_key.replace("_", " ").title())


def list_model_entries() -> list[ArtifactModelEntry]:
    entries: list[ArtifactModelEntry] = []

    runtime = get_latest_runtime_evaluation()
    if runtime is not None:
        entries.append(
            ArtifactModelEntry(
                model_version=runtime["model_version"],
                model_type=runtime.get("model_type", "rule-based"),
                title="Runtime scoring baseline",
                evaluation_status=runtime.get("evaluation_status", "unknown"),
                generated_at=runtime.get("evaluated_at"),
                summary="Current in-app scoring baseline used by the invoice risk queue.",
                limitations=runtime.get("limitations", []),
                metrics=None,
                artifact_path=str(_latest_json(EVALUATIONS_DIR)),
                dataset_key="runtime",
                approved_for_runtime=True,
            )
        )

    native = get_latest_native_artifact()
    if native is not None:
        entries.append(
            ArtifactModelEntry(
                model_version=native["model_version"],
                model_type=native.get("model_type", "logistic_regression"),
                title="Project-native workflow demo",
                evaluation_status=native.get("evaluation_status", "unknown"),
                generated_at=native.get("generated_at"),
                summary=native.get("small_dataset_warning", "Native ML artifact for readiness evaluation."),
                limitations=native.get("limitations", []),
                metrics=native.get("metrics"),
                artifact_path=str(_latest_json(PROJECT_NATIVE_DIR)),
                dataset_key="native",
                approved_for_runtime=False,
            )
        )

    comparison = get_comparison_artifact()
    if comparison is not None:
        for dataset_key, metric_key in ((comparison.get("dataset_a"), "metric_a"), (comparison.get("dataset_b"), "metric_b")):
            if not dataset_key:
                continue
            entries.append(
                ArtifactModelEntry(
                    model_version=f"benchmark-{dataset_key}",
                    model_type="logistic_regression",
                    title=_humanize_dataset_key(dataset_key),
                    evaluation_status="BENCHMARK_REFERENCE",
                    generated_at=None,
                    summary=(
                        f"External benchmark summary. Headline comparison metric: {comparison.get(metric_key)}. "
                        "Useful for benchmarking and feature-discovery, not runtime replacement."
                    ),
                    limitations=[
                        "External benchmark results do not validate runtime scoring fit for this app.",
                        "Transfer ideas, not model weights.",
                    ],
                    metrics={"headline_metric": comparison.get(metric_key)},
                    artifact_path=str(COMPARISON_PATH),
                    dataset_key=dataset_key,
                    approved_for_runtime=False,
                )
            )

    return entries
