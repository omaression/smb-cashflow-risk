"""IBM pipeline entrypoint."""

from __future__ import annotations

import csv
from pathlib import Path

from app.ml.adapters import IBMInvoiceAdapter
from app.ml.config import RunConfig
from app.ml.training import train_dataset_pipeline


def run_ibm_pipeline(raw_csv_path: str | Path, output_dir: str | Path, config: RunConfig):
    path = Path(raw_csv_path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    adapter = IBMInvoiceAdapter()
    batch = adapter.normalize_rows(rows)
    adapter.persist_cached_snapshot(Path(output_dir), batch.frame)
    return train_dataset_pipeline("ibm", list(batch.rows), config, Path(output_dir))
