#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

API_ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.ingestion import ingest_csv_file
from app.models import Customer, DailyCashSnapshot, Invoice, Payment  # noqa: F401
from app.ml.config import RunConfig
from app.ml.pipelines import NativePipelineDeferred, run_project_native_pipeline


def _bootstrap_sample_sqlite_db() -> Session:
    tmp_dir = Path(tempfile.mkdtemp(prefix="smb-cashflow-risk-native-ml-"))
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
    db = _bootstrap_sample_sqlite_db()
    output_dir = PROJECT_ROOT / "artifacts" / "ml" / "project_native"
    try:
        try:
            manifest = run_project_native_pipeline(db, output_dir, RunConfig())
            print(f"trained: {manifest.metrics_path}")
        except NativePipelineDeferred as exc:
            print(str(exc))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
