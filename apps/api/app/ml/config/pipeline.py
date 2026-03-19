"""Configuration schema for the dual-dataset ML scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LeakagePolicy:
    """Column-level rules to drop post-target information."""

    forbid_columns: tuple[str, ...] = (
        "paid_date",
        "days_late",
        "is_delinquent",
        "settled_date",
        "clear_date",
        "days_to_settle",
        "paperless_date",
        "is_open",
    )
    drop_target_from_features: bool = True
    holdout_method: str = "temporal"


@dataclass(frozen=True)
class RunConfig:
    """Run-level options for one dataset training job."""

    model_name: str = "logistic-baseline"
    target_name: str = "is_late_15"
    random_seed: int = 42
    test_size: float = 0.2
    validation_size: float = 0.2
    max_features: int = 512
    min_rows_for_train: int = 200
    min_positive_rows: int = 25
    leakage_policy: LeakagePolicy = field(default_factory=LeakagePolicy)
