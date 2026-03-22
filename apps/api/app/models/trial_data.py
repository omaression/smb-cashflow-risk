"""
Trial-scoped data models for BYOD workspaces.

These models store imported customer, invoice, payment, and cash snapshot data
scoped to a trial workspace. They mirror the demo data models but include
workspace_id foreign keys for isolation.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TrialCustomer(Base):
    """Customer data imported into a trial workspace."""

    __tablename__ = "trial_customer"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False, index=True)
    external_customer_id: Mapped[str | None] = mapped_column(Text, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(128))
    segment: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64))
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)

    workspace = relationship("TrialWorkspace", back_populates="customers")
    invoices = relationship("TrialInvoice", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("TrialPayment", back_populates="customer", cascade="all, delete-orphan")


class TrialInvoice(Base):
    """Invoice data imported into a trial workspace."""

    __tablename__ = "trial_invoice"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_customer.id"), nullable=False, index=True)
    external_invoice_id: Mapped[str | None] = mapped_column(Text, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="sent")
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    workspace = relationship("TrialWorkspace", back_populates="invoices")
    customer = relationship("TrialCustomer", back_populates="invoices")
    payments = relationship("TrialPayment", back_populates="invoice", cascade="all, delete-orphan")


class TrialPayment(Base):
    """Payment data imported into a trial workspace."""

    __tablename__ = "trial_payment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False, index=True)
    external_payment_id: Mapped[str | None] = mapped_column(Text, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_customer.id"), nullable=False, index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_invoice.id"), nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(64))

    workspace = relationship("TrialWorkspace", back_populates="payments")
    customer = relationship("TrialCustomer", back_populates="payments")
    invoice = relationship("TrialInvoice", back_populates="payments")


class TrialCashSnapshot(Base):
    """Cash snapshot data imported into a trial workspace."""

    __tablename__ = "trial_cash_snapshot"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trial_workspace.id"), nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    workspace = relationship("TrialWorkspace", back_populates="cash_snapshots")