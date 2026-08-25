"""Physical book copy — a single accessioned item on the shelf."""
from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, new_uuid


class CopyStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ISSUED = "ISSUED"
    RESERVED = "RESERVED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"
    MAINTENANCE = "MAINTENANCE"


# Valid state transitions for a book copy. Anything not listed here is rejected
# by CirculationService._transition_copy().
ALLOWED_COPY_TRANSITIONS: dict[CopyStatus, set[CopyStatus]] = {
    CopyStatus.AVAILABLE: {CopyStatus.ISSUED, CopyStatus.RESERVED, CopyStatus.LOST, CopyStatus.DAMAGED, CopyStatus.MAINTENANCE},
    CopyStatus.ISSUED: {CopyStatus.AVAILABLE, CopyStatus.LOST, CopyStatus.DAMAGED},
    CopyStatus.RESERVED: {CopyStatus.ISSUED, CopyStatus.AVAILABLE},
    CopyStatus.LOST: {CopyStatus.AVAILABLE, CopyStatus.MAINTENANCE},
    CopyStatus.DAMAGED: {CopyStatus.AVAILABLE, CopyStatus.MAINTENANCE},
    CopyStatus.MAINTENANCE: {CopyStatus.AVAILABLE},
}


class BookCopy(TimestampMixin, Base):
    __tablename__ = "book_copies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    accession_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[CopyStatus] = mapped_column(Enum(CopyStatus), default=CopyStatus.AVAILABLE, nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition: Mapped[str] = mapped_column(String(50), default="GOOD")

    book = relationship("Book", back_populates="copies")
