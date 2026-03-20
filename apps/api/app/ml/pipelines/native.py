"""Project-native pipeline entrypoint."""

from __future__ import annotations

from pathlib import Path

from app.ml.adapters import ProjectNativeInvoiceAdapter
from app.ml.config import RunConfig
from app.ml.reporting.project_native import write_native_workflow_demo


class NativePipelineDeferred(Exception):
    """Raised when the native dataset is too small for honest training."""


def run_project_native_pipeline(session, output_dir: str | Path, config: RunConfig):
    output = Path(output_dir)
    adapter = ProjectNativeInvoiceAdapter()
    batch = adapter.build_from_session(session)
    adapter.persist_cached_snapshot(output, batch.frame)

    row_count = len(batch.rows)
    positive_count = int(batch.frame[config.target_name].sum()) if not batch.frame.empty else 0
    if row_count < config.min_rows_for_train or positive_count < config.min_positive_rows:
        json_path, md_path = write_native_workflow_demo(
            output,
            row_count=row_count,
            positive_count=positive_count,
            min_rows_required=config.min_rows_for_train,
        )
        raise NativePipelineDeferred(f"Deferred training; workflow demo written to {json_path} and {md_path}")

    return train_dataset_pipeline("native", list(batch.rows), config, output)
