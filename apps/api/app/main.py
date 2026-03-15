from fastapi import FastAPI

from app.config import settings
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.invoices import router as invoices_router

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(invoices_router, prefix=settings.api_prefix)
