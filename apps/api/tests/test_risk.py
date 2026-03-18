"""Tests for risk scoring service."""
from datetime import date
from decimal import Decimal
import uuid

from app.models import Customer, Invoice
from app.services.risk import score_invoice, _clamp_probability


def _create_test_customer(db_session, name: str, payment_terms_days: int | None = 30, external_customer_id: str | None = None) -> Customer:
    """Helper to create a customer with proper field names."""
    if external_customer_id is None:
        external_customer_id = f"CUST-TEST-{uuid.uuid4().hex[:8]}"
    customer = Customer(
        external_customer_id=external_customer_id,
        name=name,
        payment_terms_days=payment_terms_days,
    )
    db_session.add(customer)
    db_session.flush()
    return customer


def _create_test_invoice(db_session, customer: Customer, total_amount: Decimal, outstanding_amount: Decimal, due_date: date, status: str = "unpaid", payment_terms_days: int | None = None, external_invoice_id: str | None = None) -> Invoice:
    """Helper to create an invoice with proper field names."""
    if external_invoice_id is None:
        external_invoice_id = f"INV-TEST-{uuid.uuid4().hex[:8]}"
    invoice = Invoice(
        external_invoice_id=external_invoice_id,
        customer_id=customer.id,
        invoice_date=date(2024, 11, 1),
        due_date=due_date,
        currency="USD",
        subtotal_amount=total_amount,
        total_amount=total_amount,
        outstanding_amount=outstanding_amount,
        status=status,
        payment_terms_days=payment_terms_days,
    )
    db_session.add(invoice)
    db_session.flush()
    return invoice


def test_score_invoice_high_risk_overdue_large_amount(db_session) -> None:
    """High-risk invoice: overdue + large amount + no payments."""
    customer = _create_test_customer(db_session, "Test Customer", payment_terms_days=30)
    invoice = _create_test_invoice(
        db_session,
        customer,
        total_amount=Decimal("15000.00"),
        outstanding_amount=Decimal("15000.00"),
        due_date=date(2024, 12, 1),
    )

    as_of = date(2025, 1, 15)  # 45 days overdue
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)

    assert bucket == "high"
    assert probability >= Decimal("0.75")
    assert "invoice_overdue_days" in reasons
    assert "customer_concentration_risk" in reasons
    assert "no_partial_payments_recorded" in reasons
    assert "call accounts payable" in action


def test_score_invoice_medium_risk_extended_terms(db_session) -> None:
    """Medium-risk: extended payment terms (45+) with moderate amount."""
    customer = _create_test_customer(db_session, "Medium Risk Customer", payment_terms_days=60)
    invoice = _create_test_invoice(
        db_session,
        customer,
        total_amount=Decimal("5000.00"),
        outstanding_amount=Decimal("5000.00"),
        due_date=date(2025, 1, 1),
        payment_terms_days=60,  # Also set on invoice to ensure extended terms component
    )

    as_of = date(2025, 1, 10)  # 9 days overdue
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)

    assert bucket == "medium"
    assert probability >= Decimal("0.50")
    assert "extended_payment_terms" in reasons
    assert "send reminder" in action


def test_score_invoice_low_risk_on_time(db_session) -> None:
    """Low-risk: not yet due, standard terms, partial payment made."""
    customer = _create_test_customer(db_session, "Low Risk Customer", payment_terms_days=30)
    invoice = _create_test_invoice(
        db_session,
        customer,
        total_amount=Decimal("3000.00"),
        outstanding_amount=Decimal("1500.00"),
        due_date=date(2025, 2, 1),
        status="partially_paid",
    )

    as_of = date(2025, 1, 15)  # Not yet due
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)

    assert bucket == "low"
    assert probability < Decimal("0.50")
    assert "keep in normal collections" in action


def test_clamp_probability_bounds() -> None:
    """Probabilities are clamped to [0.05, 0.95]."""
    assert _clamp_probability(Decimal("0.01")) == Decimal("0.05")
    assert _clamp_probability(Decimal("0.99")) == Decimal("0.95")
    assert _clamp_probability(Decimal("0.50")) == Decimal("0.50")


def test_score_invoice_uses_customer_terms_fallback(db_session) -> None:
    """Invoice can use customer payment terms if invoice terms not set."""
    customer = _create_test_customer(db_session, "Fallback Terms Customer", payment_terms_days=45)
    invoice = _create_test_invoice(
        db_session,
        customer,
        total_amount=Decimal("8000.00"),
        outstanding_amount=Decimal("8000.00"),
        due_date=date(2025, 1, 1),
        payment_terms_days=None,  # Falls back to customer terms
    )

    as_of = date(2025, 1, 5)
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)

    # Customer has 45-day terms, which triggers extended_payment_terms component
    assert "extended_payment_terms" in reasons


def test_score_invoice_reasons_limited_to_three(db_session) -> None:
    """Reasons list is capped at 3 items."""
    customer = _create_test_customer(db_session, "Many Reasons Customer", payment_terms_days=60)
    invoice = _create_test_invoice(
        db_session,
        customer,
        total_amount=Decimal("20000.00"),
        outstanding_amount=Decimal("20000.00"),
        due_date=date(2024, 12, 1),
        payment_terms_days=60,
    )

    as_of = date(2025, 1, 20)  # Overdue, large, extended terms, no payments
    probability, bucket, reasons, action = score_invoice(invoice, customer, as_of)

    # Would have 4+ potential reasons but capped at 3
    assert len(reasons) <= 3