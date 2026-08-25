"""Fine model — a monetary penalty tied to a loan."""
from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, new_uuid


class FineStatus(str, enum.Enum):
    OUTSTANDING = "OUTSTANDING"
    PAID = "PAID"
    WAIVED = "WAIVED"


class Fine(TimestampMixin, Base):
    __tablename__ = "fines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), default="Overdue return")
    status: Mapped[FineStatus] = mapped_column(Enum(FineStatus), default=FineStatus.OUTSTANDING, nullable=False)
    settled_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    loan = relationship("Loan")
    member = relationship("User")
