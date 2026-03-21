from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.model_version import CURRENT_MODEL_VERSION


def _find_artifacts_root() -> Path:
    current = Path(__file__).resolve()

    for candidate in [current.parent, *current.parents]:
        artifacts_dir = candidate / "artifacts"
        if artifacts_dir.is_dir():
            return artifacts_dir

    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        artifacts_dir = candidate / "artifacts"
        if artifacts_dir.is_dir():
            return artifacts_dir

    # Safe fallback: point at a non-existent but well-formed local path so the
    # service degrades gracefully instead of crashing app import on deployments
    # that do not ship artifact files.
    return current.parent / "artifacts"


ARTIFACTS_ROOT = _find_artifacts_root()
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
    if not directory.exists():
        return None
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
    latest_runtime_path = _latest_json(EVALUATIONS_DIR)
    entries.append(
        ArtifactModelEntry(
            model_version=CURRENT_MODEL_VERSION.version,
            model_type=CURRENT_MODEL_VERSION.model_type,
            title="Runtime scoring baseline",
            evaluation_status=(runtime or {}).get("evaluation_status", CURRENT_MODEL_VERSION.evaluation_status),
            generated_at=(runtime or {}).get("evaluated_at"),
            summary="Current in-app scoring baseline used by the invoice risk queue.",
            limitations=(runtime or {}).get("limitations", CURRENT_MODEL_VERSION.notes),
            metrics=None,
            artifact_path=str(latest_runtime_path) if latest_runtime_path else "",
            dataset_key="runtime",
            approved_for_runtime=True,
        )
    )

    native = get_latest_native_artifact()
    latest_native_path = _latest_json(PROJECT_NATIVE_DIR)
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
                artifact_path=str(latest_native_path) if latest_native_path else "",
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
