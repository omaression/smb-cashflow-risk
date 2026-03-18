#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

API_ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.database import Base
from app.ingestion import ingest_csv_file
from app.models import Customer, DailyCashSnapshot, Invoice, Payment  # noqa: F401
from app.services.scoring import build_and_export_features


def _bootstrap_sample_sqlite_db() -> Session:
    tmp_dir = Path(tempfile.mkdtemp(prefix="smb-cashflow-risk-"))
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
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "data" / "processed" / "invoice_features.csv"
    db = _bootstrap_sample_sqlite_db()
    try:
        written_path = build_and_export_features(db, output_path)
    finally:
        db.close()

    print(written_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
