#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

API_ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
except ModuleNotFoundError as exc:
    missing = exc.name or "required dependency"
    print(
        f"Missing Python dependency: {missing}. Run this script from the API virtualenv "
        f"(for example: 'cd apps/api && . .venv/bin/activate && cd ../.. && python3 scripts/evaluate-baseline.py').",
        file=sys.stderr,
    )
    raise SystemExit(1)

from app.database import Base
from app.ingestion import ingest_csv_file
from app.models import Customer, DailyCashSnapshot, Invoice, Payment  # noqa: F401
from app.services.evaluation import generate_evaluation_report, save_evaluation_artifact, score_and_evaluate_split, split_features
from app.services.features import build_invoice_feature_rows
from app.services.model_version import CURRENT_MODEL_VERSION


def _bootstrap_sample_sqlite_db() -> Session:
    tmp_dir = Path(tempfile.mkdtemp(prefix="smb-cashflow-risk-eval-"))
    engine = create_engine(f"sqlite:///{tmp_dir / 'demo.db'}", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    data_dir = PROJECT_ROOT / "data" / "raw"
    db = SessionLocal()
    ingest_csv_file("customers", (data_dir / "sample_customers.csv").read_bytes(), db)
    ingest_csv_file("invoices", (data_dir / "sample_invoices.csv").read_bytes(), db)
    ingest_csv_file("payments", (data_dir / "sample_payments.csv").read_bytes(), db)
    ingest_csv_file("cash_snapshots", (data_dir / "sample_cash_snapshots.csv").read_bytes(), db)
    return db


def main() -> int:
    artifact_dir = PROJECT_ROOT / "artifacts" / "evaluations"
    db = _bootstrap_sample_sqlite_db()
    try:
        rows = build_invoice_feature_rows(db)
        split = split_features(rows)
        results = {}
        for split_name, split_rows in {
            "train": split.train,
            "validation": split.validation,
            "test": split.test,
        }.items():
            _, evaluation = score_and_evaluate_split(split_rows, split_name)
            results[split_name] = evaluation

        limitations = [
            "Weights are heuristic and were not learned from historical optimization.",
            "Current sample size is too small for statistically meaningful model metrics.",
            "Scores should not be interpreted as calibrated probabilities.",
            "This artifact demonstrates workflow readiness, not validated predictive performance.",
        ]
        json_path = save_evaluation_artifact(
            artifact_dir,
            CURRENT_MODEL_VERSION,
            results,
            small_dataset_warning=split.warning,
            limitations=limitations,
        )
        report_path = generate_evaluation_report(
            artifact_dir,
            CURRENT_MODEL_VERSION,
            results,
            small_dataset_warning=split.warning,
            limitations=limitations,
        )
    finally:
        db.close()

    print(f"artifact: {json_path}")
    print(f"report:   {report_path}")
    for name, result in results.items():
        print(f"{name}: rows={result.row_count} status={result.metrics_status} accuracy={result.accuracy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
