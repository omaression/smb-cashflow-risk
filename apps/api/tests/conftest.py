from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.database import Base, get_db
from app.models import Customer, DailyCashSnapshot, Invoice, Payment  # noqa: F401
from app.main import app
from app.ingestion import ingest_csv_file

TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_data(db_session: Session) -> Generator[Session, None, None]:
    """Load sample CSV data into the test database."""
    ingest_csv_file("customers", (DATA_DIR / "sample_customers.csv").read_bytes(), db_session)
    ingest_csv_file("invoices", (DATA_DIR / "sample_invoices.csv").read_bytes(), db_session)
    ingest_csv_file("payments", (DATA_DIR / "sample_payments.csv").read_bytes(), db_session)
    ingest_csv_file("cash_snapshots", (DATA_DIR / "sample_cash_snapshots.csv").read_bytes(), db_session)
    yield db_session
