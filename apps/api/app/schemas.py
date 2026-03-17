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


class DashboardSummaryResponse(BaseModel):
    total_ar: float
    overdue_ar: float
    open_invoice_count: int
    risky_invoice_count: int
    top_risky_customers: list[str]
    projected_cash_balances: dict[str, float]


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
