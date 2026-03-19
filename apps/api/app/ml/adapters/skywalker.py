"""Skywalker invoice dataset adapter."""

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from app.ml.adapters.base import BaseInvoiceDatasetAdapter, DatasetBatch


class SkywalkerInvoiceAdapter(BaseInvoiceDatasetAdapter):
    """Adapter for the Skywalker raw invoice dataset."""

    source_hint = "https://raw.githubusercontent.com/SkywalkerHub/Payment-Date-Prediction/main/Dataset.csv"
    target_key = "is_late_15"

    @classmethod
    def source_schema(cls) -> str:
        return "skywalker-invoices-v1"

    def normalize_rows(self, rows: Iterable[dict[str, Any]]) -> DatasetBatch:
        frame = pd.DataFrame(list(rows)).copy()
        frame.columns = [str(col).strip() for col in frame.columns]
        frame["invoice_date"] = pd.to_datetime(frame["posting_date"], errors="coerce")
        frame["due_date"] = pd.to_datetime(frame["due_in_date"], format="%Y%m%d.%f", errors="coerce")
        frame["settled_date"] = pd.to_datetime(frame["clear_date"], errors="coerce")
        frame["amount"] = pd.to_numeric(frame["total_open_amount"], errors="coerce")
        frame["customer_id"] = frame["cust_number"].astype(str)
        frame["invoice_id"] = frame["invoice_id"].astype(str)
        frame["currency"] = frame["invoice_currency"].astype(str)
        frame["payment_terms"] = frame["cust_payment_terms"].astype(str)
        frame["is_open"] = pd.to_numeric(frame["isOpen"], errors="coerce").fillna(0).astype(int)
        frame["days_to_due"] = (frame["due_date"] - frame["invoice_date"]).dt.days
        frame = frame[frame["invoice_date"].notna() & frame["due_date"].notna() & frame["settled_date"].notna()].copy()
        frame["days_late"] = (frame["settled_date"] - frame["due_date"]).dt.days.fillna(0)
        frame["days_late"] = frame["days_late"].clip(lower=0)
        frame["is_late_1"] = (frame["days_late"] >= 1).astype(int)
        frame["is_late_5"] = (frame["days_late"] >= 5).astype(int)
        frame["is_late_15"] = (frame["days_late"] >= 15).astype(int)
        frame["dataset"] = "skywalker"
        normalized = frame[
            [
                "dataset",
                "invoice_id",
                "customer_id",
                "invoice_date",
                "due_date",
                "settled_date",
                "amount",
                "currency",
                "payment_terms",
                "days_to_due",
                "days_late",
                "is_open",
                "is_late_1",
                "is_late_5",
                "is_late_15",
            ]
        ].copy()
        return DatasetBatch(rows=normalized.to_dict(orient="records"), frame=normalized)
