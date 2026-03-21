from app.ingestion.role_mapping import suggest_field_mappings


def test_suggests_required_fields_for_invoices() -> None:
    headers = ["invoice_id", "customer_id", "invoice_date", "due_date", "amount"]
    result = suggest_field_mappings(role="invoices", headers=headers)

    canon_map = {field.canonical_field: field for field in result.field_mappings}

    assert canon_map["external_invoice_id"].source_field == "invoice_id"
    assert canon_map["external_invoice_id"].resolved is True
    assert canon_map["external_invoice_id"].required is True
    assert "external_customer_id" in canon_map
    assert "total_amount" in canon_map


def test_detects_required_missing_fields() -> None:
    headers = ["invoice_date", "amount"]
    result = suggest_field_mappings(role="invoices", headers=headers)

    missing = set(result.required_missing)
    assert "external_invoice_id" in missing
    assert "external_customer_id" in missing
    assert "due_date" in missing


def test_flags_ambiguity_when_multiple_headers_map_to_same_canonical() -> None:
    headers = ["invoice", "invoice_no", "customer", "due_date", "amount"]
    result = suggest_field_mappings(role="invoices", headers=headers)

    canon_map = {field.canonical_field: field for field in result.field_mappings}
    assert canon_map["external_invoice_id"].resolved is False
    assert len(canon_map["external_invoice_id"].alternatives) >= 1
    assert any("Multiple columns" in warning for warning in result.ambiguity_warnings)


def test_unpaid_invoice_export_mapping() -> None:
    headers = ["invoice", "customer", "invoice_date", "due_date", "amount_due"]
    result = suggest_field_mappings(role="unpaid_invoice_export", headers=headers)

    canon_map = {field.canonical_field: field for field in result.field_mappings}

    assert canon_map["external_invoice_id"].source_field == "invoice"
    assert canon_map["customer_name"].source_field == "customer"
    assert canon_map["due_date"].source_field == "due_date"
    assert canon_map["outstanding_amount"].source_field == "amount_due"
    assert result.required_missing == []