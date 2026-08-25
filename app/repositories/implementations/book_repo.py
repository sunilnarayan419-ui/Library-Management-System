from __future__ import annotations

from sqlalchemy import or_, select

from app.models.book import Book
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class BookRepository(SQLAlchemyRepository[Book]):
    model = Book

    def search(
        self,
        query: str | None = None,
        category: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Book], int]:
        stmt = select(Book)
        if query:
            like = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    Book.title.ilike(like) if hasattr(Book.title, "ilike") else Book.title.like(like),
                    Book.author.ilike(like) if hasattr(Book.author, "ilike") else Book.author.like(like),
                    Book.isbn.like(like),
                )
            )
        if category:
            stmt = stmt.where(Book.category == category)

        total = len(self.db.execute(stmt).scalars().all())
        stmt = stmt.offset(offset).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def get_by_isbn(self, isbn: str) -> Book | None:
        stmt = select(Book).where(Book.isbn == isbn)
        return self.db.execute(stmt).scalars().first()
