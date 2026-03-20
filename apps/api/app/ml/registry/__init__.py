"""Dataset registry metadata for ML pipelines."""

from dataclasses import dataclass, field
from typing import Dict

from app.ml.adapters import IBMInvoiceAdapter, ProjectNativeInvoiceAdapter, SkywalkerInvoiceAdapter


@dataclass(frozen=True)
class DatasetSpec:
    """Metadata used by the ML dataset registry."""

    key: str
    name: str
    description: str
    adapter_cls: type
    source_hint: str
    target_column: str = "is_late_15"
    holdout_required: bool = True
    labels: list[str] = field(default_factory=list)


DatasetKey = str


_DATASETS: Dict[DatasetKey, DatasetSpec] = {
    "native": DatasetSpec(
        key="native",
        name="Project Native Invoice Features",
        description="Workflow-ready project-native feature rows generated from the repo's own invoice schema.",
        adapter_cls=ProjectNativeInvoiceAdapter,
        source_hint="app.services.features.build_invoice_feature_rows",
        labels=["is_late_15"],
    ),
    "ibm": DatasetSpec(
        key="ibm",
        name="IBM ML Invoice Delay",
        description="External invoice dataset from the IBM benchmark family.",
        adapter_cls=IBMInvoiceAdapter,
        source_hint="../uploads/20260319_091134_AgADHAcAArMx4EU.csv",
        labels=["is_late_1", "is_late_5", "is_late_15", "days_late"],
    ),
    "skywalker": DatasetSpec(
        key="skywalker",
        name="Skywalker Invoice Ledger",
        description="External invoice/payment dataset for a second independent baseline.",
        adapter_cls=SkywalkerInvoiceAdapter,
        source_hint="https://raw.githubusercontent.com/SkywalkerHub/Payment-Date-Prediction/main/Dataset.csv",
        labels=["is_late_1", "is_late_5", "is_late_15", "days_late"],
    ),
}


def list_dataset_keys() -> list[DatasetKey]:
    """Return available dataset keys."""
    return sorted(_DATASETS.keys())


def get_dataset_spec(dataset_key: DatasetKey) -> DatasetSpec:
    """Fetch the registry entry for a dataset key."""
    return _DATASETS[dataset_key]
