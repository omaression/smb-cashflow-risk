"""Skywalker pipeline entrypoint."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from urllib.request import urlopen

from app.ml.adapters import SkywalkerInvoiceAdapter
from app.ml.config import RunConfig
from app.ml.training import train_dataset_pipeline


def run_skywalker_pipeline(raw_csv_url: str, output_dir: str | Path, config: RunConfig):
    text = urlopen(raw_csv_url, timeout=30).read().decode("utf-8", errors="replace")
    rows = list(csv.DictReader(io.StringIO(text)))
    adapter = SkywalkerInvoiceAdapter()
    batch = adapter.normalize_rows(rows)
    adapter.persist_cached_snapshot(Path(output_dir), batch.frame)
    return train_dataset_pipeline("skywalker", list(batch.rows), config, Path(output_dir))
