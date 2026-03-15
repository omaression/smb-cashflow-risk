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


class CashForecastResponse(BaseModel):
    as_of_date: str
    horizon_days: int
    base_balance: float
    expected_inflows: float
    downside_inflows: float
    projected_outflows: float
    projected_closing_balance: float
    downside_closing_balance: float


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
