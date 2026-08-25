from __future__ import annotations

from sqlalchemy import select

from app.models.book_copy import BookCopy, CopyStatus
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class BookCopyRepository(SQLAlchemyRepository[BookCopy]):
    model = BookCopy

    def first_available_for_book(self, book_id: str) -> BookCopy | None:
        stmt = (
            select(BookCopy)
            .where(BookCopy.book_id == book_id, BookCopy.status == CopyStatus.AVAILABLE)
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()

    def get_by_accession(self, accession_number: str) -> BookCopy | None:
        stmt = select(BookCopy).where(BookCopy.accession_number == accession_number)
        return self.db.execute(stmt).scalars().first()
