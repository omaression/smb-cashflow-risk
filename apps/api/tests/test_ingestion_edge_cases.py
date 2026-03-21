"""Edge case and additional coverage tests for previously merged ingestion modules."""

import pytest

from app.ingestion.file_roles import FileRoleDetection, detect_file_role, _normalize_token, _read_headers_and_count
from app.ingestion.role_mapping import RoleMappingResult, suggest_field_mappings


class TestFileRolesEdgeCases:
    def test_detect_file_role_with_unicode_headers(self) -> None:
        contents = b"INV-\xc3\x96123,Customer Name,Due Date,Amount\n1,Test,2026-03-21,100\n"
        detection = detect_file_role(filename="invoices.csv", contents=contents)
        assert detection.role in {"invoices", "unpaid_invoice_export"}
        assert detection.row_count == 1

    def test_detect_file_role_with_extra_whitespace(self) -> None:
        contents = b"  Invoice #  ,  Customer  ,  Due Date  ,  Amount Due  \nINV-1,Acme,2026-03-21,1000\n"
        detection = detect_file_role(filename="export.csv", contents=contents)
        assert detection.role == "unpaid_invoice_export"
        assert "invoice" in [h for h in detection.headers if h.startswith("invoice")]

    def test_detect_file_role_empty_file(self) -> None:
        contents = b""
        detection = detect_file_role(filename="empty.csv", contents=contents)
        assert detection.role is None
        assert detection.row_count == 0
        assert detection.confidence == 0.0

    def test_detect_file_role_headers_only_no_rows(self) -> None:
        contents = b"Invoice,Customer,Due Date,Amount\n"
        detection = detect_file_role(filename="headers_only.csv", contents=contents)
        # Headers only should still detect role based on headers
        assert detection.role in {"invoices", "unpaid_invoice_export"}
        assert detection.row_count == 0

    def test_detect_file_role_alternative_role_ranking(self) -> None:
        # File with payment-like columns but also invoice columns
        contents = b"Payment ID,Invoice,Customer,Payment Date,Amount Paid\nPAY-1,INV-1,Acme,2026-03-21,500\n"
        detection = detect_file_role(filename="payments.csv", contents=contents)
        assert detection.role == "payments"
        assert len(detection.alternatives) >= 1

    def test_detect_file_role_bom_prefixed_utf8(self) -> None:
        # UTF-8 BOM
        contents = b"\xef\xbb\xbfInvoice,Customer,Due Date,Amount\nINV-1,Acme,2026-03-21,1000\n"
        detection = detect_file_role(filename="bom.csv", contents=contents)
        assert detection.role in {"invoices", "unpaid_invoice_export"}
        assert detection.row_count == 1

    def test_normalized_token_removes_punctuation(self) -> None:
        assert _normalize_token("Invoice #") == "invoice"
        assert _normalize_token("Due-Date") == "due_date"
        assert _normalize_token("Customer.Name") == "customer_name"

    def test_read_headers_and_count_latin1_fallback(self) -> None:
        # Latin-1 content that isn't valid UTF-8
        contents = b"Invoice,Customer,Caf\xe9\n1,A,Test\n"
        headers, count = _read_headers_and_count(contents)
        assert headers == ["invoice", "customer", "caf"]
        assert count == 1

    def test_detect_file_role_confidence_increases_with_more_matches(self) -> None:
        # Minimal headers
        contents1 = b"Invoice,Due Date\nINV-1,2026-03-21\n"
        detection1 = detect_file_role(filename="minimal.csv", contents=contents1)

        # More headers
        contents2 = b"Invoice,Customer,Due Date,Amount,Status\nINV-1,Acme,2026-03-21,1000,Open\n"
        detection2 = detect_file_role(filename="fuller.csv", contents=contents2)

        assert detection2.confidence >= detection1.confidence


class TestRoleMappingEdgeCases:
    def test_suggest_field_mappings_empty_headers(self) -> None:
        result = suggest_field_mappings(role="invoices", headers=[])
        assert all(f.source_field is None for f in result.field_mappings if f.required)
        assert len(result.required_missing) > 0

    def test_suggest_field_mappings_with_whitespace_in_headers(self) -> None:
        headers = ["  Invoice ID  ", " Customer Name ", " Due Date ", " Amount "]
        result = suggest_field_mappings(role="invoices", headers=headers)
        canon_map = {f.canonical_field: f for f in result.field_mappings}
        assert canon_map["external_invoice_id"].source_field == "invoice_id"
        assert canon_map["due_date"].source_field == "due_date"

    def test_suggest_field_mappings_case_insensitive(self) -> None:
        headers = ["INVOICE NUMBER", "customer", "DUE DATE", "TOTAL AMOUNT"]
        result = suggest_field_mappings(role="invoices", headers=headers)
        canon_map = {f.canonical_field: f for f in result.field_mappings}
        assert canon_map["external_invoice_id"].source_field == "invoice_number"
        assert canon_map["total_amount"].source_field == "total_amount"

    def test_suggest_field_mappings_unknown_role(self) -> None:
        result = suggest_field_mappings(role="unknown_role", headers=["foo", "bar"])
        assert result.role == "unknown_role"
        assert len(result.field_mappings) == 0

    def test_suggest_field_mappings_payments_role(self) -> None:
        headers = ["Payment ID", "Invoice Number", "Payment Date", "Amount"]
        result = suggest_field_mappings(role="payments", headers=headers)
        canon_map = {f.canonical_field: f for f in result.field_mappings}
        assert canon_map["external_payment_id"].source_field == "payment_id"
        assert "external_invoice_id" in [f.canonical_field for f in result.field_mappings]

    def test_suggest_field_mappings_customers_role(self) -> None:
        headers = ["Customer ID", "Customer Name", "Industry", "Credit Limit"]
        result = suggest_field_mappings(role="customers", headers=headers)
        canon_map = {f.canonical_field: f for f in result.field_mappings}
        assert canon_map["external_customer_id"].source_field == "customer_id"
        assert canon_map["name"].source_field == "customer_name"

    def test_suggest_field_mappings_cash_snapshots_role(self) -> None:
        headers = ["Snapshot Date", "Currency", "Opening Balance", "Closing Balance"]
        result = suggest_field_mappings(role="cash_snapshots", headers=headers)
        canon_map = {f.canonical_field: f for f in result.field_mappings}
        assert canon_map["snapshot_date"].source_field == "snapshot_date"
        assert canon_map["currency"].source_field == "currency"

    def test_suggest_field_mappings_all_required_present(self) -> None:
        headers = ["Invoice ID", "Customer ID", "Invoice Date", "Due Date", "Total Amount"]
        result = suggest_field_mappings(role="invoices", headers=headers)
        assert result.required_missing == []
        assert result.confidence >= 0.8

    def test_suggest_field_mappings_multiple_aliases_conflict(self) -> None:
        # Multiple columns could map to same canonical field
        headers = ["Invoice", "Invoice No", "Invoice Number", "Customer", "Due Date"]
        result = suggest_field_mappings(role="invoices", headers=headers)
        assert any("Multiple columns" in w for w in result.ambiguity_warnings)

    def test_suggest_field_mappings_partial_required(self) -> None:
        headers = ["Invoice ID", "Customer Name"]  # Missing dates and amount
        result = suggest_field_mappings(role="invoices", headers=headers)
        assert "invoice_date" in result.required_missing
        assert "due_date" in result.required_missing
        assert "total_amount" in result.required_missing