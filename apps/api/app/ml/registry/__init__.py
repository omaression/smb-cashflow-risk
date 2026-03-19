"""Dataset registry metadata for ML pipelines."""

from dataclasses import dataclass, field
from typing import Dict

from app.ml.adapters import IBMInvoiceAdapter, SkywalkerInvoiceAdapter


@dataclass(frozen=True)
class DatasetSpec:
    """Metadata used by the dual-dataset adapter registry."""

    key: str
    name: str
    description: str
    adapter_cls: type
    source_hint: str
    target_column: str = "is_delinquent"
    holdout_required: bool = True
    labels: list[str] = field(default_factory=list)


DatasetKey = str


_DATASETS: Dict[DatasetKey, DatasetSpec] = {
    "ibm": DatasetSpec(
        key="ibm",
        name="IBM ML Invoice Delay",
        description="External invoice dataset from the IBM benchmark family.",
        adapter_cls=IBMInvoiceAdapter,
        source_hint="raw_data/external/ibm",
        labels=["is_delinquent", "days_late", "days_to_term"],
    ),
    "skywalker": DatasetSpec(
        key="skywalker",
        name="Skywalker Invoice Ledger",
        description="External invoice/payment dataset for a second independent baseline.",
        adapter_cls=SkywalkerInvoiceAdapter,
        source_hint="raw_data/external/skywalker",
        labels=["is_delinquent", "days_late", "overdue_ratio"],
    ),
}


def list_dataset_keys() -> list[DatasetKey]:
    """Return available dataset keys."""
    return sorted(_DATASETS.keys())


def get_dataset_spec(dataset_key: DatasetKey) -> DatasetSpec:
    """Fetch the registry entry for a dataset key."""
    return _DATASETS[dataset_key]
