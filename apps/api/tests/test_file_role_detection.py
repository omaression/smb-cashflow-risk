from app.ingestion.file_roles import detect_file_role


def test_detects_unpaid_invoice_export_from_headers() -> None:
    contents = b"Invoice #,Customer,Due Date,Amount Due,Status\nINV-1,Acme,2026-03-01,1250,Open\n"
    detection = detect_file_role(filename="open-ar-aging.csv", contents=contents)

    assert detection.role == "unpaid_invoice_export"
    assert detection.confidence >= 0.5
    assert detection.row_count == 1
    assert detection.reasons


def test_detects_payments_file_from_headers() -> None:
    contents = b"Payment ID,Invoice Number,Payment Date,Amount Paid,Reference\nPAY-1,INV-1,2026-03-05,500,RMT-22\n"
    detection = detect_file_role(filename="payments-export.csv", contents=contents)

    assert detection.role == "payments"
    assert detection.confidence >= 0.4


def test_returns_none_when_headers_are_too_ambiguous() -> None:
    contents = b"foo,bar,baz\n1,2,3\n"
    detection = detect_file_role(filename="mystery.csv", contents=contents)

    assert detection.role is None
    assert detection.confidence == 0.0
