import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyCashSnapshot(Base):
    __tablename__ = "daily_cash_snapshot"
    __table_args__ = (UniqueConstraint("snapshot_date", "currency"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    cash_in: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    cash_out: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
