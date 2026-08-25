"""Book model — the conceptual/catalog record (not a physical copy)."""
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, new_uuid


class Book(TimestampMixin, Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(50), default="English")

    copies = relationship("BookCopy", back_populates="book", cascade="all, delete-orphan")

    @property
    def total_copies(self) -> int:
        return len(self.copies)

    @property
    def available_copies(self) -> int:
        from app.models.book_copy import CopyStatus

        return sum(1 for c in self.copies if c.status == CopyStatus.AVAILABLE)
