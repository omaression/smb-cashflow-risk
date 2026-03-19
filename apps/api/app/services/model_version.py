from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ModelType = Literal["rule-based", "logistic"]

SCORING_PARAMETERS = {
    "base_score": 0.30,
    "overdue_days_weight": 0.012,
    "max_overdue_days": 60,
    "extended_terms_penalty": 0.07,
    "extended_terms_threshold": 45,
    "large_invoice_penalty": 0.08,
    "large_invoice_threshold": 10000.0,
    "no_partial_payments_penalty": 0.10,
    "partial_payments_penalty": 0.04,
    "customer_late_ratio_weight": 0.12,
    "min_score": 0.05,
    "max_score": 0.95,
    "high_risk_threshold": 0.75,
    "medium_risk_threshold": 0.50,
}

FEATURES_USED = [
    "overdue_days",
    "payment_terms_days",
    "amount",
    "paid_ratio",
    "customer_late_invoice_ratio",
]


@dataclass(frozen=True)
class ModelVersion:
    version: str
    model_type: ModelType
    target: str
    decision_threshold: float
    features_used: list[str]
    scoring_parameters: dict[str, float | int]
    description: str
    evaluation_status: str
    notes: list[str]


CURRENT_MODEL_VERSION = ModelVersion(
    version="v0.1.0-rules",
    model_type="rule-based",
    target="is_late_15",
    decision_threshold=0.50,
    features_used=FEATURES_USED,
    scoring_parameters=SCORING_PARAMETERS,
    description="Rule-based baseline for SMB cash-flow risk MVP. Weights are heuristic, not learned from historical data.",
    evaluation_status="WORKFLOW_DEMO",
    notes=[
        "Current sample data is too small for statistically meaningful model metrics.",
        "Scores are heuristic and should not be interpreted as calibrated probabilities.",
        "This version exists to demonstrate reproducible ML workflow structure and artifact generation.",
    ],
)
