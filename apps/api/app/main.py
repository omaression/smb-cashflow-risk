import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import (  # noqa: F401 — ensure models registered
    Customer,
    DailyCashSnapshot,
    DataQualityProfile,
    ImportFile,
    ImportJob,
    Invoice,
    Payment,
    TrialWorkspace,
)

logger = logging.getLogger(__name__)
from app.routers.customers import router as customers_router
from app.routers.dashboard import router as dashboard_router
from app.routers.forecast import router as forecast_router
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router
from app.routers.invoices import router as invoices_router
from app.routers.ml import router as ml_router
from app.routers.root import router as root_router
from app.routers.trial import router as trial_router
from app.routers.trial_dashboard import router as trial_dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        logger.warning("Could not create tables on startup (expected in test/CI)")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(root_router)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(invoices_router, prefix=settings.api_prefix)
app.include_router(customers_router, prefix=settings.api_prefix)
app.include_router(forecast_router, prefix=settings.api_prefix)
app.include_router(ingest_router, prefix=settings.api_prefix)
app.include_router(ml_router, prefix=settings.api_prefix)
app.include_router(trial_router, prefix=settings.api_prefix)
app.include_router(trial_dashboard_router, prefix=settings.api_prefix)
