from __future__ import annotations

import json
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.trial_workspace import DataQualityProfile, ImportFile, ImportJob, TrialWorkspace


def create_preview_workspace(session: Session, *, filenames: list[str]) -> TrialWorkspace:
    workspace = TrialWorkspace(
        label="BYOD preview workspace",
        status="preview_ready",
        source_type="upload",
        data_quality_score=Decimal("56.00"),
        confidence_score=Decimal("48.00"),
        warning_count=2,
    )
    session.add(workspace)
    session.flush()

    import_job = ImportJob(
        workspace_id=workspace.id,
        status="preview_ready",
        source_file_count=len(filenames),
        preview_issue_count=1,
        preview_warning_count=2,
        error_summary_json=json.dumps(
            {
                "fatal": 0,
                "high": 1 if filenames else 0,
                "medium": 1 if filenames else 0,
                "low": 1 if filenames else 0,
            }
        ),
    )
    session.add(import_job)
    session.flush()

    for filename in filenames:
        session.add(
            ImportFile(
                import_job_id=import_job.id,
                filename=filename,
                detected_role="unpaid_invoice_export",
                detection_confidence=Decimal("72.00"),
                row_count=0,
                parse_warnings_json=json.dumps([
                    "Column mapping is still provisional until preview confirmation.",
                ]),
                mapping_json=json.dumps(
                    {
                        "invoice_id": {"source": "Invoice #", "confidence": 0.84},
                        "customer_name": {"source": "Customer", "confidence": 0.79},
                        "due_date": {"source": "Due Date", "confidence": 0.88},
                        "outstanding_amount": {"source": "Amount Due", "confidence": 0.81},
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
                    "medium": 1,
                    "low": 1,
                }
            ),
        )
    )

    session.commit()
    session.refresh(workspace)
    return workspace


def get_workspace(session: Session, workspace_id: UUID) -> TrialWorkspace | None:
    return session.get(TrialWorkspace, workspace_id)
