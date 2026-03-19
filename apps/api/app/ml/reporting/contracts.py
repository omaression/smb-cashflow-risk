"""Contracts for side-by-side model comparison reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from app.ml.training.runner import ModelRunManifest


@dataclass(frozen=True)
class ComparisonResult:
    dataset_a: str
    dataset_b: str
    metric_a: float
    metric_b: float
    winner: str
    report_md_path: Path | None = None
    report_json_path: Path | None = None


def default_comparison_columns() -> list[str]:
    return [
        "dataset",
        "rows",
        "roc_auc",
        "pr_auc",
        "precision",
        "recall",
        "f1",
        "model_version",
        "notes",
    ]


def write_comparison_report(output_dir: Path, manifest_a: ModelRunManifest, manifest_b: ModelRunManifest) -> ComparisonResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    winner = manifest_a.dataset_key if manifest_a.f1 >= manifest_b.f1 else manifest_b.dataset_key
    result = ComparisonResult(
        dataset_a=manifest_a.dataset_key,
        dataset_b=manifest_b.dataset_key,
        metric_a=manifest_a.f1,
        metric_b=manifest_b.f1,
        winner=winner,
        report_md_path=output_dir / "comparison.md",
        report_json_path=output_dir / "comparison.json",
    )
    md = f"# Dual-Dataset Logistic Baseline Comparison\n\n| Dataset | Rows | ROC-AUC | PR-AUC | Precision | Recall | F1 |\n|---|---:|---:|---:|---:|---:|---:|\n| {manifest_a.dataset_key} | {manifest_a.rows_processed} | {manifest_a.roc_auc} | {manifest_a.pr_auc} | {manifest_a.precision} | {manifest_a.recall} | {manifest_a.f1} |\n| {manifest_b.dataset_key} | {manifest_b.rows_processed} | {manifest_b.roc_auc} | {manifest_b.pr_auc} | {manifest_b.precision} | {manifest_b.recall} | {manifest_b.f1} |\n\n## Honest notes\n- Metrics compare two external-dataset pipelines, not production transferability to smb-cashflow-risk.\n- Leakage controls and target definitions must be reviewed before trusting any winner.\n- Higher metric score does not automatically mean better project-fit.\n- A larger dataset can look better simply because it provides more stable supervision, not because it is closer to our app domain.\n- Validation is used only for threshold selection; the reported metrics come from the held-out test split.\n\nWinner by F1: **{winner}**\n"
    result.report_md_path.write_text(md, encoding="utf-8")
    result.report_json_path.write_text(json.dumps(asdict(result), indent=2, default=str), encoding="utf-8")
    return result
