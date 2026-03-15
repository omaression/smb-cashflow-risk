import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    external_invoice_id: Mapped[str | None] = mapped_column(Text, unique=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customer.id"), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")
