from __future__ import annotations

import json
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.ingestion.file_roles import detect_file_role
from app.ingestion.role_mapping import suggest_field_mappings
from app.models.trial_workspace import DataQualityProfile, ImportFile, ImportJob, TrialWorkspace


def create_preview_workspace(session: Session, *, uploads: list[tuple[str, bytes]]) -> TrialWorkspace:
    detections = [detect_file_role(filename=filename, contents=contents) for filename, contents in uploads]
    warning_count = sum(1 for detection in detections if detection.confidence < 0.7)

    workspace = TrialWorkspace(
        label="BYOD preview workspace",
        status="preview_ready",
        source_type="upload",
        data_quality_score=Decimal("56.00"),
        confidence_score=Decimal("48.00"),
        warning_count=warning_count,
    )
    session.add(workspace)
    session.flush()

    import_job = ImportJob(
        workspace_id=workspace.id,
        status="preview_ready",
        source_file_count=len(uploads),
        preview_issue_count=1 if uploads else 0,
        preview_warning_count=warning_count,
        error_summary_json=json.dumps(
            {
                "fatal": 0,
                "high": 1 if uploads else 0,
                "medium": warning_count,
                "low": len(uploads),
            }
        ),
    )
    session.add(import_job)
    session.flush()

    for (filename, _contents), detection in zip(uploads, detections, strict=False):
        role = detection.role or "unknown"
        mapping = suggest_field_mappings(role=role, headers=detection.headers)
        field_payload = {
            field.canonical_field: {
                "source": field.source_field,
                "confidence": field.confidence,
                "required": field.required,
                "resolved": field.resolved,
                "alternatives": field.alternatives,
            }
            for field in mapping.field_mappings
        }
        field_payload["_alternatives"] = [
            {"role": role, "confidence": score} for role, score in detection.alternatives
        ]
        session.add(
            ImportFile(
                import_job_id=import_job.id,
                filename=filename,
                detected_role=detection.role,
                detection_confidence=Decimal(str(detection.confidence * 100)) if detection.confidence else None,
                row_count=detection.row_count,
                parse_warnings_json=json.dumps(
                    detection.reasons
                    + mapping.ambiguity_warnings
                    + ["Column mapping is still provisional until preview confirmation."]
                ),
                mapping_json=json.dumps(field_payload),
                profiling_json=json.dumps(
                    {
                        "headers": detection.headers,
                        "reasons": detection.reasons,
                        "required_missing": mapping.required_missing,
                    }
                ),
            )
        )

    session.add(
        DataQualityProfile(
            workspace_id=workspace.id,
            completeness_score=Decimal("58.00"),
            consistency_score=Decimal("63.00"),
            coverage_score=Decimal("54.00"),
            history_depth_score=Decimal("35.00"),
            sample_size_score=Decimal("42.00"),
            overall_confidence_score=Decimal("48.00"),
            reliability_grade="low",
            recommendations_json=json.dumps(
                [
                    "Add payment history columns or a separate payments file to improve reliability.",
                    "Provide stable customer identifiers to reduce name-based entity resolution risk.",
                    "Include a fresher as-of snapshot or open balance export to improve forecast trust.",
                ]
            ),
            issue_summary_json=json.dumps(
                {
                    "fatal": 0,
                    "high": 1,
                    "medium": warning_count,
                    "low": len(uploads),
                }
            ),
        )
    )

    session.commit()
    session.refresh(workspace)
    return workspace


def get_workspace(session: Session, workspace_id: UUID) -> TrialWorkspace | None:
    return session.get(TrialWorkspace, workspace_id)
