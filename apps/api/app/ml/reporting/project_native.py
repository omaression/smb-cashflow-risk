"""Project-native workflow-demo reporting helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json


def write_native_workflow_demo(output_dir: Path, *, row_count: int, positive_count: int, min_rows_required: int) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"v0.2.0-native-workflow-demo_{timestamp}.json"
    md_path = output_dir / f"v0.2.0-native-workflow-demo_{timestamp}.md"

    payload = {
        "model_version": "v0.2.0-native-workflow-demo",
        "model_type": "logistic_regression",
        "target": "is_late_15",
        "evaluation_status": "WORKFLOW_DEMO",
        "row_count": row_count,
        "positive_count": positive_count,
        "minimum_rows_required": min_rows_required,
        "small_dataset_warning": (
            f"Only {row_count} native rows are available. This artifact demonstrates pipeline readiness, "
            "not meaningful predictive performance."
        ),
        "metrics": None,
        "limitations": [
            "Project-native sample is too small for meaningful model training.",
            "No honest train/validation/test comparison can be claimed at this size.",
            "This artifact exists to prove adapter/pipeline/report readiness only.",
            "Runtime scoring should remain rule-based until enough native data exists.",
        ],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(
        "# Project-Native ML Workflow Demo\n\n"
        "## ⚠️ Limitations First\n"
        f"Only {row_count} project-native rows are available, with {positive_count} positive examples. "
        "That is not enough for a meaningful learned-model evaluation.\n\n"
        "## What this proves\n"
        "- native adapter works\n"
        "- native pipeline wiring works\n"
        "- artifact/report generation works\n\n"
        "## What this does not prove\n"
        "- logistic regression outperforms the rule-based scorer\n"
        "- any meaningful project-native predictive power\n"
        "- readiness to replace runtime scoring\n",
        encoding="utf-8",
    )
    return json_path, md_path
