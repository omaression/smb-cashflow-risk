from datetime import date

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class IngestRowError(BaseModel):
    row_number: int
    message: str


class IngestResponse(BaseModel):
    entity_type: str
    imported: int
    updated: int
    rejected: int
    errors: list[IngestRowError]


class TopRiskyCustomer(BaseModel):
    id: str
    name: str


class DashboardSummaryResponse(BaseModel):
    total_ar: float
    overdue_ar: float
    open_invoice_count: int
    risky_invoice_count: int
    top_risky_customers: list[TopRiskyCustomer]
    projected_cash_balances: dict[str, float]
    runtime_model_version: str | None = None
    ml_status_badge: str | None = None


class InvoiceRiskItem(BaseModel):
    invoice_id: str
    customer_name: str
    amount: float
    due_date: date
    overdue_days: int
    late_payment_probability: float
    risk_bucket: str
    top_reason_codes: list[str]
    recommended_action: str


class CashForecastPoint(BaseModel):
    forecast_date: date
    projected_balance: float
    expected_inflows: float
    expected_outflows: float


class CashForecastResponse(BaseModel):
    horizon_days: int
    scenario: str
    currency: str
    starting_balance: float
    series: list[CashForecastPoint]


class PaymentHistoryItemResponse(BaseModel):
    payment_date: date
    amount: float
    payment_method: str | None
    reference: str | None


class InvoiceDetailResponse(BaseModel):
    invoice_id: str
    customer_id: str
    customer_name: str
    invoice_date: date
    due_date: date
    currency: str
    total_amount: float
    outstanding_amount: float
    amount_paid: float
    status: str
    overdue_days: int
    payment_history: list[PaymentHistoryItemResponse]
    late_payment_probability: float
    risk_bucket: str
    top_reason_codes: list[str]
    recommended_action: str
    model_version: str | None = None
    score_type: str | None = None


class CustomerOpenInvoiceResponse(BaseModel):
    invoice_id: str
    total_amount: float
    outstanding_amount: float
    due_date: date
    status: str
    late_payment_probability: float
    risk_bucket: str


class CustomerDetailResponse(BaseModel):
    customer_id: str
    customer_name: str
    industry: str | None
    segment: str | None
    payment_terms_days: int | None
    credit_limit: float | None
    open_exposure: float
    open_invoice_count: int
    overdue_invoice_count: int
    average_days_overdue: float
    late_payment_ratio: float
    top_recommendation: str
    open_invoices: list[CustomerOpenInvoiceResponse]


class FieldMappingResponse(BaseModel):
    canonical_field: str
    source_field: str | None = None
    confidence: float = 0.0
    required: bool = False
    resolved: bool = False
    alternatives: list[str] = []


class PreviewFileDetectionResponse(BaseModel):
    filename: str
    detected_role: str | None
    detection_confidence: float | None
    row_count: int
    headers: list[str]
    detection_reasons: list[str]
    parse_warnings: list[str]
    suggested_mapping: dict[str, dict[str, str | float | bool | list[str] | None]]
    alternative_roles: list[dict[str, str | float]] = []
    required_missing: list[str] = []
    ambiguity_warnings: list[str] = []


class TrialQualityProfileResponse(BaseModel):
    completeness_score: float | None
    consistency_score: float | None
    coverage_score: float | None
    history_depth_score: float | None
    sample_size_score: float | None
    overall_confidence_score: float | None
    reliability_grade: str | None
    recommendations: list[str]
    issue_summary: dict[str, int]


class ImportPreviewResponse(BaseModel):
    workspace_id: str
    status: str
    source_file_count: int
    files: list[PreviewFileDetectionResponse]
    quality_profile: TrialQualityProfileResponse


class TrialWorkspaceStatusResponse(BaseModel):
    workspace_id: str
    label: str
    status: str
    source_type: str
    warning_count: int
    data_quality_score: float | None
    confidence_score: float | None
    quality_profile: TrialQualityProfileResponse | None
