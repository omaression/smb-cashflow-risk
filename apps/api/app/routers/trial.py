import json
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ImportPreviewResponse,
    PreviewFileDetectionResponse,
    TrialQualityProfileResponse,
    TrialWorkspaceStatusResponse,
)
from app.services.trial_workspaces import create_preview_workspace, get_workspace

router = APIRouter(prefix="/trial", tags=["trial"])


def _quality_payload(workspace) -> TrialQualityProfileResponse | None:
    profile = workspace.quality_profile
    if profile is None:
        return None
    return TrialQualityProfileResponse(
        completeness_score=float(profile.completeness_score) if profile.completeness_score is not None else None,
        consistency_score=float(profile.consistency_score) if profile.consistency_score is not None else None,
        coverage_score=float(profile.coverage_score) if profile.coverage_score is not None else None,
        history_depth_score=float(profile.history_depth_score) if profile.history_depth_score is not None else None,
        sample_size_score=float(profile.sample_size_score) if profile.sample_size_score is not None else None,
        overall_confidence_score=float(profile.overall_confidence_score) if profile.overall_confidence_score is not None else None,
        reliability_grade=profile.reliability_grade,
        recommendations=json.loads(profile.recommendations_json or "[]"),
        issue_summary=json.loads(profile.issue_summary_json or "{}"),
    )


@router.post("/preview", response_model=ImportPreviewResponse)
def preview_import(files: list[UploadFile] = File(...), db: Session = Depends(get_db)) -> ImportPreviewResponse:
    if not files:
        raise HTTPException(status_code=400, detail="at least one file is required")

    workspace = create_preview_workspace(
        db,
        uploads=[(file.filename or "upload.csv", file.file.read()) for file in files],
    )
    latest_job = workspace.import_jobs[-1]

    preview_files = []
    for file in latest_job.files:
        mapping_payload = json.loads(file.mapping_json or "{}")
        profiling_payload = json.loads(file.profiling_json or "{}")
        alternative_roles = mapping_payload.pop("_alternatives", [])
        preview_files.append(
            PreviewFileDetectionResponse(
                filename=file.filename,
                detected_role=file.detected_role,
                detection_confidence=float(file.detection_confidence) if file.detection_confidence is not None else None,
                row_count=file.row_count,
                headers=profiling_payload.get("headers", []),
                detection_reasons=profiling_payload.get("reasons", []),
                parse_warnings=json.loads(file.parse_warnings_json or "[]"),
                suggested_mapping=mapping_payload,
                alternative_roles=alternative_roles,
                required_missing=profiling_payload.get("required_missing", []),
                ambiguity_warnings=[
                    warning for warning in json.loads(file.parse_warnings_json or "[]")
                    if "Multiple columns map to" in warning
                ],
            )
        )

    quality = _quality_payload(workspace)
    assert quality is not None

    return ImportPreviewResponse(
        workspace_id=str(workspace.id),
        status=workspace.status,
        source_file_count=latest_job.source_file_count,
        files=preview_files,
        quality_profile=quality,
    )


@router.get("/{workspace_id}/status", response_model=TrialWorkspaceStatusResponse)
def trial_status(workspace_id: UUID, db: Session = Depends(get_db)) -> TrialWorkspaceStatusResponse:
    workspace = get_workspace(db, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail=f"trial workspace not found: {workspace_id}")

    return TrialWorkspaceStatusResponse(
        workspace_id=str(workspace.id),
        label=workspace.label,
        status=workspace.status,
        source_type=workspace.source_type,
        warning_count=workspace.warning_count,
        data_quality_score=float(workspace.data_quality_score) if workspace.data_quality_score is not None else None,
        confidence_score=float(workspace.confidence_score) if workspace.confidence_score is not None else None,
        quality_profile=_quality_payload(workspace),
    )
