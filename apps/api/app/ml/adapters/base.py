"""Base interfaces shared by all external dataset adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd


@dataclass(frozen=True)
class DatasetBatch:
    """Simple typed container for normalized rows."""

    rows: Sequence[dict[str, Any]]
    frame: pd.DataFrame


class BaseInvoiceDatasetAdapter:
    """Adapter contract for one dataset -> normalized batch conversion."""

    source_hint: str = ""
    target_key: str = "is_delinquent"

    @classmethod
    def source_schema(cls) -> str:
        return "unverified"

    def normalize_rows(self, rows: Iterable[dict[str, Any]]) -> DatasetBatch:
        frame = pd.DataFrame(list(rows))
        return DatasetBatch(rows=frame.to_dict(orient="records"), frame=frame)

    def validate_schema(self, rows: Sequence[dict[str, Any]]) -> None:
        """No-op validation hook for pipeline-level checks."""
        _ = rows

    def persist_cached_snapshot(self, output_dir: Path, frame: pd.DataFrame) -> Path:
        """Persist normalized data to csv for portability."""
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact = output_dir / "normalized.csv"
        frame.to_csv(artifact, index=False)
        return artifact
