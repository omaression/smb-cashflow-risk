from fastapi import APIRouter, HTTPException

from app.services.ml_registry import (
    build_benchmark_payload,
    build_ml_overview_payload,
    build_model_catalog_payload,
    build_native_readiness_payload,
    get_model_detail_payload,
)

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/overview")
def get_ml_overview() -> dict:
    return build_ml_overview_payload()


@router.get("/models")
def list_models() -> list[dict]:
    return build_model_catalog_payload()


@router.get("/models/{model_version}")
def get_model(model_version: str) -> dict:
    payload = get_model_detail_payload(model_version)
    if payload is None:
        raise HTTPException(status_code=404, detail=f"model not found: {model_version}")
    return payload


@router.get("/benchmarks")
def get_benchmarks() -> list[dict]:
    return build_benchmark_payload()


@router.get("/native-readiness")
def get_native_readiness() -> dict:
    return build_native_readiness_payload()
