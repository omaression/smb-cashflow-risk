import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TrialWorkspace(Base):
    __tablename__ = "trial_workspace"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="preview")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="upload")
    currency_mode: Mapped[str | None] = mapped_column(String(16))
    data_quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    import_jobs = relationship("ImportJob", back_populates="workspace", cascade="all, delete-orphan")
    quality_profile = relationship("DataQualityProfile", back_populates="workspace", uselist=False, cascade="all, delete-orphan")


class ImportJob(Base):
    __tablename__ = "import_job"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="preview_ready")
    source_file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    preview_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    preview_warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_summary_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    workspace = relationship("TrialWorkspace", back_populates="import_jobs")
    files = relationship("ImportFile", back_populates="import_job", cascade="all, delete-orphan")


class ImportFile(Base):
    __tablename__ = "import_file"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    import_job_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("import_job.id"), nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    detected_role: Mapped[str | None] = mapped_column(String(64))
    detection_confidence: Mapped[float | None] = mapped_column(Numeric(5, 2))
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parse_warnings_json: Mapped[str | None] = mapped_column(Text)
    mapping_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    import_job = relationship("ImportJob", back_populates="files")


class DataQualityProfile(Base):
    __tablename__ = "data_quality_profile"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False, unique=True)
    completeness_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    consistency_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    coverage_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    history_depth_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    sample_size_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    overall_confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    reliability_grade: Mapped[str | None] = mapped_column(String(32))
    recommendations_json: Mapped[str | None] = mapped_column(Text)
    issue_summary_json: Mapped[str | None] = mapped_column(Text)

    workspace = relationship("TrialWorkspace", back_populates="quality_profile")
