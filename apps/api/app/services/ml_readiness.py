from __future__ import annotations

from dataclasses import dataclass

from app.ml.config.pipeline import RunConfig


@dataclass(frozen=True)
class NativeReadinessSummary:
    status: str
    row_count: int
    positive_count: int
    min_rows_required: int
    min_positive_rows_required: int
    reason: str
    blockers: list[str]
    next_unlock_condition: str


_DEFAULT_REASON = "Project-native learned scoring remains deferred until enough native invoice history exists."


def build_native_readiness_summary(*, row_count: int, positive_count: int, config: RunConfig | None = None) -> NativeReadinessSummary:
    cfg = config or RunConfig()
    blockers: list[str] = []

    if row_count < cfg.min_rows_for_train:
        blockers.append(f"Need at least {cfg.min_rows_for_train} native rows; only {row_count} are available.")
    if positive_count < cfg.min_positive_rows:
        blockers.append(
            f"Need at least {cfg.min_positive_rows} positive late-payment examples; only {positive_count} are available."
        )

    if blockers:
        status = "deferred"
        reason = _DEFAULT_REASON
    else:
        status = "ready_for_training"
        reason = "Native dataset has cleared the minimum row and positive-label thresholds for honest baseline training."

    next_unlock_condition = (
        f"Reach at least {cfg.min_rows_for_train} native rows and {cfg.min_positive_rows} positive late-payment examples."
    )

    return NativeReadinessSummary(
        status=status,
        row_count=row_count,
        positive_count=positive_count,
        min_rows_required=cfg.min_rows_for_train,
        min_positive_rows_required=cfg.min_positive_rows,
        reason=reason,
        blockers=blockers,
        next_unlock_condition=next_unlock_condition,
    )
