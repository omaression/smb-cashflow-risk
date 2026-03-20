from pathlib import Path
import tempfile

from app.ml.adapters import ProjectNativeInvoiceAdapter
from app.ml.config import RunConfig
from app.ml.pipelines import NativePipelineDeferred, run_project_native_pipeline
from app.services.features import build_invoice_feature_rows


def test_project_native_adapter_builds_rows(seed_data) -> None:
    batch = ProjectNativeInvoiceAdapter().build_from_session(seed_data)

    assert len(batch.rows) == 3
    assert 'is_late_15' in batch.frame.columns
    assert 'overdue_days' in batch.frame.columns
    assert batch.frame['invoice_id'].nunique() == 3


def test_project_native_runner_defers_training_on_tiny_data(seed_data) -> None:
    output_dir = Path(tempfile.mkdtemp(prefix='native-ml-test-'))
    try:
        try:
            run_project_native_pipeline(seed_data, output_dir, RunConfig())
        except NativePipelineDeferred as exc:
            message = str(exc)
        else:
            raise AssertionError('Expected NativePipelineDeferred')
    finally:
        pass

    assert 'Deferred training' in message
    assert any(path.name.endswith('.json') for path in output_dir.iterdir())
    assert any(path.name.endswith('.md') for path in output_dir.iterdir())


def test_project_native_feature_rows_are_too_small_for_training(seed_data) -> None:
    rows = build_invoice_feature_rows(seed_data)
    assert len(rows) == 3
    assert sum(row.is_late_15 for row in rows) <= 1
