from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Customer, DailyCashSnapshot, Invoice, Payment


def test_customer_invoice_payment_relationships(db_session) -> None:
    customer = Customer(external_customer_id="CUST-001", name="Northstar")
    db_session.add(customer)
    db_session.flush()

    invoice = Invoice(
        external_invoice_id="INV-001",
        customer_id=customer.id,
        invoice_date=date(2026, 1, 1),
        due_date=date(2026, 1, 31),
        currency="USD",
        subtotal_amount=Decimal("100.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("100.00"),
        outstanding_amount=Decimal("100.00"),
        status="sent",
        payment_terms_days=30,
    )
    db_session.add(invoice)
    db_session.flush()

    payment = Payment(
        external_payment_id="PAY-001",
        invoice_id=invoice.id,
        customer_id=customer.id,
        payment_date=date(2026, 1, 20),
        amount=Decimal("100.00"),
        currency="USD",
    )
    db_session.add(payment)
    db_session.commit()

    assert customer.invoices[0].external_invoice_id == "INV-001"
    assert invoice.payments[0].external_payment_id == "PAY-001"


def test_unique_snapshot_date_currency_constraint(db_session) -> None:
    first = DailyCashSnapshot(
        snapshot_date=date(2026, 3, 1),
        currency="USD",
        opening_balance=Decimal("1000.00"),
        cash_in=Decimal("100.00"),
        cash_out=Decimal("50.00"),
        closing_balance=Decimal("1050.00"),
    )
    second = DailyCashSnapshot(
        snapshot_date=date(2026, 3, 1),
        currency="USD",
        opening_balance=Decimal("1000.00"),
        cash_in=Decimal("100.00"),
        cash_out=Decimal("50.00"),
        closing_balance=Decimal("1050.00"),
    )
    db_session.add(first)
    db_session.commit()
    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.commit()
