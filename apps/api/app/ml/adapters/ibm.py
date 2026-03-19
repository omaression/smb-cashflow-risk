"""IBM invoice dataset adapter."""

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from app.ml.adapters.base import BaseInvoiceDatasetAdapter, DatasetBatch


class IBMInvoiceAdapter(BaseInvoiceDatasetAdapter):
    """Adapter for the uploaded IBM/Kaggle invoice dataset."""

    source_hint = "../uploads/20260319_091134_AgADHAcAArMx4EU.csv"
    target_key = "is_late_15"

    @classmethod
    def source_schema(cls) -> str:
        return "ibm-invoices-v1"

    def normalize_rows(self, rows: Iterable[dict[str, Any]]) -> DatasetBatch:
        frame = pd.DataFrame(list(rows)).copy()
        frame.columns = [str(col).strip() for col in frame.columns]
        frame["invoice_date"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
        frame["due_date"] = pd.to_datetime(frame["DueDate"], errors="coerce")
        frame["settled_date"] = pd.to_datetime(frame["SettledDate"], errors="coerce")
        frame = frame[frame["invoice_date"].notna() & frame["due_date"].notna()].copy()
        frame = frame[frame["invoice_date"] <= frame["due_date"]].copy()
        frame["amount"] = pd.to_numeric(frame["InvoiceAmount"], errors="coerce")
        frame["days_late"] = pd.to_numeric(frame["DaysLate"], errors="coerce")
        frame["days_to_settle"] = pd.to_numeric(frame["DaysToSettle"], errors="coerce")
        frame["customer_id"] = frame["customerID"].astype(str)
        frame["invoice_id"] = frame["invoiceNumber"].astype(str)
        frame["country_code"] = frame["countryCode"].astype(str)
        frame["paperless_bill"] = frame["PaperlessBill"].astype(str)
        frame["disputed"] = (frame["Disputed"].astype(str).str.lower() == "yes").astype(int)
        frame["days_to_due"] = (frame["due_date"] - frame["invoice_date"]).dt.days
        frame["is_open"] = 0
        frame["is_late_1"] = (frame["days_late"] >= 1).astype(int)
        frame["is_late_5"] = (frame["days_late"] >= 5).astype(int)
        frame["is_late_15"] = (frame["days_late"] >= 15).astype(int)
        frame["dataset"] = "ibm"
        normalized = frame[
            [
                "dataset",
                "invoice_id",
                "customer_id",
                "invoice_date",
                "due_date",
                "settled_date",
                "amount",
                "country_code",
                "paperless_bill",
                "disputed",
                "days_to_due",
                "days_to_settle",
                "days_late",
                "is_open",
                "is_late_1",
                "is_late_5",
                "is_late_15",
            ]
        ].copy()
        return DatasetBatch(rows=normalized.to_dict(orient="records"), frame=normalized)
