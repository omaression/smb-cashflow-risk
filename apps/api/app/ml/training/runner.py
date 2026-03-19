"""Training/evaluation runner for external dataset logistic baselines."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.config import RunConfig


@dataclass(frozen=True)
class ModelRunManifest:
    dataset_key: str
    model_version: str
    rows_processed: int
    train_rows: int
    val_rows: int
    test_rows: int
    positive_rate_train: float
    positive_rate_test: float
    roc_auc: float
    pr_auc: float
    precision: float
    recall: float
    f1: float
    metrics_path: Path | None = None
    model_path: Path | None = None


def split_dataset_rows(
    frame: pd.DataFrame,
    test_size: float,
    val_size: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values("invoice_date").reset_index(drop=True)

    years = ordered["invoice_date"].dt.year.dropna().unique().tolist()
    if len(years) >= 2:
        years = sorted(years)
        train = ordered[ordered["invoice_date"].dt.year == years[0]].copy()
        later = ordered[ordered["invoice_date"].dt.year != years[0]].copy()
        if len(later) >= 2 and len(train) >= max(200, int(len(ordered) * 0.2)):
            midpoint = max(1, len(later) // 2)
            validation = later.iloc[:midpoint].copy()
            test = later.iloc[midpoint:].copy()
            if not train.empty and not validation.empty and not test.empty:
                return train, validation, test

    n = len(ordered)
    test_n = max(1, int(round(n * test_size)))
    val_n = max(1, int(round(n * val_size)))
    if test_n + val_n >= n:
        test_n = max(1, n // 5)
        val_n = max(1, n // 5)
    train_end = n - test_n - val_n
    val_end = n - test_n
    return ordered.iloc[:train_end].copy(), ordered.iloc[train_end:val_end].copy(), ordered.iloc[val_end:].copy()


def _feature_columns(frame: pd.DataFrame, target_name: str, forbidden: tuple[str, ...]) -> tuple[list[str], list[str]]:
    candidate = [
        col for col in frame.columns
        if col not in {target_name, "dataset", "invoice_id", "customer_id"}
        and col not in set(forbidden)
    ]
    numeric = [col for col in candidate if pd.api.types.is_numeric_dtype(frame[col])]
    categorical = [col for col in candidate if col not in numeric]
    return numeric, categorical


def _build_pipeline(numeric_cols: list[str], categorical_cols: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical_cols,
            ),
        ]
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])


def train_dataset_pipeline(dataset_key: str, normalized_rows: list[dict[str, Any]], config: RunConfig, output_dir: Path) -> ModelRunManifest:
    frame = pd.DataFrame(normalized_rows).dropna(subset=["invoice_date", config.target_name, "amount"])
    if len(frame) < config.min_rows_for_train:
        raise ValueError(f"Dataset {dataset_key} has only {len(frame)} rows; minimum is {config.min_rows_for_train}.")

    train_df, val_df, test_df = split_dataset_rows(frame, config.test_size, config.validation_size)
    for split_name, split_df in [("train", train_df), ("test", test_df)]:
        positives = int(split_df[config.target_name].sum())
        if positives < config.min_positive_rows:
            raise ValueError(f"Dataset {dataset_key} split {split_name} has only {positives} positive rows; minimum is {config.min_positive_rows}.")

    numeric_cols, categorical_cols = _feature_columns(frame, config.target_name, config.leakage_policy.forbid_columns)
    model = _build_pipeline(numeric_cols, categorical_cols)
    model.fit(train_df[numeric_cols + categorical_cols], train_df[config.target_name])

    test_scores = model.predict_proba(test_df[numeric_cols + categorical_cols])[:, 1]
    test_pred = (test_scores >= 0.5).astype(int)

    manifest = ModelRunManifest(
        dataset_key=dataset_key,
        model_version=f"v0.2.0-{dataset_key}-{config.model_name}",
        rows_processed=len(frame),
        train_rows=len(train_df),
        val_rows=len(val_df),
        test_rows=len(test_df),
        positive_rate_train=round(float(train_df[config.target_name].mean()), 4),
        positive_rate_test=round(float(test_df[config.target_name].mean()), 4),
        roc_auc=round(float(roc_auc_score(test_df[config.target_name], test_scores)), 4),
        pr_auc=round(float(average_precision_score(test_df[config.target_name], test_scores)), 4),
        precision=round(float(precision_score(test_df[config.target_name], test_pred, zero_division=0)), 4),
        recall=round(float(recall_score(test_df[config.target_name], test_pred, zero_division=0)), 4),
        f1=round(float(f1_score(test_df[config.target_name], test_pred, zero_division=0)), 4),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"{manifest.model_version}.joblib"
    metrics_path = output_dir / f"{manifest.model_version}.json"
    joblib.dump(model, model_path)
    finalized_manifest = ModelRunManifest(**{**asdict(manifest), "metrics_path": metrics_path, "model_path": model_path})
    metrics_path.write_text(json.dumps({**asdict(finalized_manifest), "generated_at": datetime.now(UTC).isoformat()}, indent=2, default=str), encoding="utf-8")
    return finalized_manifest
