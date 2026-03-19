"""Machine-learning package scaffolding for the dual-dataset phase."""

from .registry import DatasetKey, DatasetSpec, get_dataset_spec

__all__ = ["DatasetKey", "DatasetSpec", "get_dataset_spec"]
