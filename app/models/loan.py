"""Loan model — tracks a book copy issued to a member."""
from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, new_uuid


class LoanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    LOST = "LOST"


class Loan(TimestampMixin, Base):
    __tablename__ = "loans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    copy_id: Mapped[str] = mapped_column(ForeignKey("book_copies.id"), nullable=False, index=True)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    issued_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    issued_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
    due_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    returned_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    renewal_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)

    copy = relationship("BookCopy")
    book = relationship("Book")
    member = relationship("User", back_populates="loans", foreign_keys=[member_id])

    def is_overdue(self, as_of: dt.datetime | None = None) -> bool:
        as_of = as_of or dt.datetime.now(dt.UTC)
        due = self.due_at if self.due_at.tzinfo else self.due_at.replace(tzinfo=dt.UTC)
        return self.status in (LoanStatus.ACTIVE, LoanStatus.OVERDUE) and as_of > due
