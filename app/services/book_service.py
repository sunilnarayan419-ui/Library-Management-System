"""Book catalog management service."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import BookNotFound, DuplicateISBN, ValidationError
from app.models.book import Book
from app.models.book_copy import BookCopy
from app.models.user import User
from app.repositories.implementations.book_copy_repo import BookCopyRepository
from app.repositories.implementations.book_repo import BookRepository
from app.services.audit_service import AuditService


class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.books = BookRepository(db)
        self.copies = BookCopyRepository(db)
        self.audit = AuditService(db)

    def create_book(
        self,
        *,
        title: str,
        author: str,
        isbn: str | None = None,
        publisher: str | None = None,
        publication_year: int | None = None,
        category: str | None = None,
        description: str | None = None,
        language: str = "English",
        initial_copies: int = 1,
        actor: User | None = None,
    ) -> Book:
        if not title.strip():
            raise ValidationError("Book title cannot be empty")
        if isbn and self.books.get_by_isbn(isbn):
            raise DuplicateISBN(f"A book with ISBN '{isbn}' already exists")

        book = Book(
            title=title.strip(),
            author=author.strip(),
            isbn=isbn,
            publisher=publisher,
            publication_year=publication_year,
            category=category,
            description=description,
            language=language,
        )
        self.books.add(book)

        for i in range(initial_copies):
            self._add_copy_unchecked(book, index=i + 1)

        self.audit.record("BOOK_CREATED", "book", book.id, actor=actor, metadata={"title": title})
        return book

    def _add_copy_unchecked(self, book: Book, index: int) -> BookCopy:
        accession = f"{book.id[:8]}-{index:03d}"
        copy = BookCopy(book_id=book.id, accession_number=accession)
        self.copies.add(copy)
        return copy

    def add_copy(self, book_id: str, accession_number: str, location: str | None = None,
                 condition: str = "GOOD", actor: User | None = None) -> BookCopy:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFound(f"Book '{book_id}' not found")
        if self.copies.get_by_accession(accession_number):
            raise ValidationError(f"Accession number '{accession_number}' already in use")
        copy = BookCopy(book_id=book.id, accession_number=accession_number, location=location, condition=condition)
        self.copies.add(copy)
        self.audit.record("BOOK_COPY_ADDED", "book_copy", copy.id, actor=actor)
        return copy

    def get_book(self, book_id: str) -> Book:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFound(f"Book '{book_id}' not found")
        return book

    def search_books(self, query: str | None, category: str | None, page: int, page_size: int):
        offset = (page - 1) * page_size
        return self.books.search(query=query, category=category, offset=offset, limit=page_size)

    def update_book(self, book_id: str, actor: User | None = None, **fields) -> Book:
        book = self.get_book(book_id)
        for key, value in fields.items():
            if value is not None:
                setattr(book, key, value)
        self.db.flush()
        self.audit.record("BOOK_UPDATED", "book", book.id, actor=actor)
        return book

    def delete_book(self, book_id: str, actor: User | None = None) -> None:
        book = self.get_book(book_id)
        from app.models.book_copy import CopyStatus

        if any(c.status != CopyStatus.AVAILABLE for c in book.copies):
            raise ValidationError("Cannot delete a book with copies that are issued, reserved, or unavailable")
        self.books.delete(book)
        self.audit.record("BOOK_DELETED", "book", book_id, actor=actor)
