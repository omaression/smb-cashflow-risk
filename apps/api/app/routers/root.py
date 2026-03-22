"""API root endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
def root():
    """Return API metadata and useful links."""
    return {
        "name": "SMB Cashflow Risk API",
        "version": "v0.5.0",
        "docs": "/docs",
        "summary": "/api/v1/dashboard/summary",
        "ml_evidence": "/api/v1/ml/overview",
        "trial_preview": "/api/v1/trial/preview",
    }