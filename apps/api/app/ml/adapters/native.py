"""Project-native dataset adapter for ML workflow readiness."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Iterable

import pandas as pd
from sqlalchemy.orm import Session

from app.ml.adapters.base import BaseInvoiceDatasetAdapter, DatasetBatch
from app.services.features import InvoiceFeatureRow, build_invoice_feature_rows


class ProjectNativeInvoiceAdapter(BaseInvoiceDatasetAdapter):
    """Adapter for the repo's own invoice feature table."""

    source_hint = "project-native-feature-builder"
    target_key = "is_late_15"

    @classmethod
    def source_schema(cls) -> str:
        return "project-native-invoice-features-v1"

    def build_from_session(self, session: Session) -> DatasetBatch:
        rows = build_invoice_feature_rows(session)
        normalized = [self._normalize_row(row) for row in rows]
        frame = pd.DataFrame(normalized)
        return DatasetBatch(rows=normalized, frame=frame)

    def normalize_rows(self, rows: Iterable[dict]) -> DatasetBatch:
        frame = pd.DataFrame(list(rows)).copy()
        return DatasetBatch(rows=frame.to_dict(orient="records"), frame=frame)

    def _normalize_row(self, row: InvoiceFeatureRow) -> dict:
        payload = asdict(row)
        payload["dataset"] = "project_native"
        payload["invoice_id"] = str(payload["invoice_id"])
        payload["customer_id"] = str(payload["customer_id"])
        payload["amount"] = float(payload["amount"] or Decimal("0"))
        payload["outstanding_amount"] = float(payload["outstanding_amount"] or Decimal("0"))
        payload["customer_total_exposure"] = float(payload["customer_total_exposure"] or Decimal("0"))
        payload["customer_open_exposure"] = float(payload["customer_open_exposure"] or Decimal("0"))
        payload["paid_amount"] = float(payload["paid_amount"] or Decimal("0"))
        payload["is_open"] = int(bool(payload["is_open"]))
        return payload
