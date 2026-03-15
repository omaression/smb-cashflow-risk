from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator


VALID_INVOICE_STATUSES = {"draft", "sent", "partially_paid", "paid", "void", "written_off"}


def _normalize_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError("invalid boolean value")


class CustomerRow(BaseModel):
    external_customer_id: str
    name: str
    industry: str | None = None
    segment: str | None = None
    country: str | None = None
    payment_terms_days: int | None = None
    credit_limit: Decimal | None = None
    is_active: bool = True

    @field_validator("external_customer_id", "name")
    @classmethod
    def non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("payment_terms_days")
    @classmethod
    def non_negative_terms(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("must be >= 0")
        return value

    @field_validator("credit_limit")
    @classmethod
    def non_negative_credit_limit(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("must be >= 0")
        return value

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value: object) -> bool:
        return _normalize_bool(value)


class InvoiceRow(BaseModel):
    external_invoice_id: str
    external_customer_id: str
    invoice_date: date
    due_date: date
    currency: str
    subtotal_amount: Decimal
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal
    outstanding_amount: Decimal
    status: Literal["draft", "sent", "partially_paid", "paid", "void", "written_off"]
    payment_terms_days: int | None = None

    @field_validator("external_invoice_id", "external_customer_id")
    @classmethod
    def invoice_fields_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("currency")
    @classmethod
    def currency_format(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("must be a 3-letter currency code")
        return value

    @field_validator("subtotal_amount", "tax_amount", "total_amount", "outstanding_amount")
    @classmethod
    def non_negative_amounts(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("must be >= 0")
        return value

    @field_validator("payment_terms_days")
    @classmethod
    def invoice_terms_non_negative(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_dates_and_amounts(self) -> "InvoiceRow":
        if self.due_date < self.invoice_date:
            raise ValueError("due_date must be on or after invoice_date")
        if self.outstanding_amount > self.total_amount:
            raise ValueError("outstanding_amount must be <= total_amount")
        return self


class PaymentRow(BaseModel):
    external_payment_id: str
    external_invoice_id: str
    external_customer_id: str
    payment_date: date
    amount: Decimal
    currency: str
    payment_method: str | None = None
    reference: str | None = None

    @field_validator("external_payment_id", "external_invoice_id", "external_customer_id")
    @classmethod
    def payment_fields_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("must be > 0")
        return value

    @field_validator("currency")
    @classmethod
    def payment_currency_format(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("must be a 3-letter currency code")
        return value


class CashSnapshotRow(BaseModel):
    snapshot_date: date
    currency: str
    opening_balance: Decimal
    cash_in: Decimal
    cash_out: Decimal
    closing_balance: Decimal

    @field_validator("currency")
    @classmethod
    def snapshot_currency_format(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("must be a 3-letter currency code")
        return value

    @model_validator(mode="after")
    def validate_balance_equation(self) -> "CashSnapshotRow":
        if self.closing_balance != self.opening_balance + self.cash_in - self.cash_out:
            raise ValueError("closing_balance must equal opening_balance + cash_in - cash_out")
        return self
