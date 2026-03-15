from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.ingestion import ingest_csv_file
from app.schemas import IngestResponse, IngestRowError

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/csv", response_model=IngestResponse)
def import_csv(
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IngestResponse:
    try:
        contents = file.file.read()
        result = ingest_csv_file(entity_type=entity_type, contents=contents, session=db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IngestResponse(
        entity_type=result.entity_type,
        imported=result.imported,
        updated=result.updated,
        rejected=result.rejected,
        errors=[IngestRowError(row_number=error.row_number, message=error.message) for error in result.errors],
    )
