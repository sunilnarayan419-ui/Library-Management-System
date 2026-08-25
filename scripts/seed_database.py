#!/usr/bin/env python
"""Populate the database with safe, fictitious development/demo data:
users (admin/librarian/members), books with copies, a few active and
historical loans, a reservation, and an audit trail.

Usage:
    python scripts/seed_database.py
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from app.core.exceptions import DuplicateEmail, DuplicateISBN
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user import UserRole
from app.services.auth_service import AuthService
from app.services.book_service import BookService
from app.services.circulation_service import CirculationService

DEMO_USERS = [
    ("Demo Admin", "admin@example.com", "AdminPass123!", UserRole.ADMIN),
    ("Demo Librarian", "librarian@example.com", "LibrarianPass123!", UserRole.LIBRARIAN),
    ("Asha Verma", "asha@example.com", "MemberPass123!", UserRole.MEMBER),
    ("Ravi Kumar", "ravi@example.com", "MemberPass123!", UserRole.MEMBER),
]

DEMO_BOOKS = [
    dict(title="Clean Code", author="Robert C. Martin", isbn="9780132350884", category="Software", initial_copies=3),
    dict(title="Domain-Driven Design", author="Eric Evans", isbn="9780321125217", category="Software", initial_copies=2),
    dict(title="Dune", author="Frank Herbert", isbn="9780441013593", category="Sci-Fi", initial_copies=2),
    dict(title="Foundation", author="Isaac Asimov", isbn="9780553293357", category="Sci-Fi", initial_copies=1),
    dict(title="Sapiens", author="Yuval Noah Harari", isbn="9780062316097", category="History", initial_copies=2),
    dict(title="The Pragmatic Programmer", author="Hunt & Thomas", isbn="9780135957059", category="Software", initial_copies=1),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        auth = AuthService(db)
        users = {}
        for name, email, password, role in DEMO_USERS:
            try:
                user = auth.register(name, email, password, role=role)
            except DuplicateEmail:
                user = auth.users.get_by_email(email)
            users[email] = user
        db.commit()

        books_svc = BookService(db)
        books = []
        for spec in DEMO_BOOKS:
            try:
                book = books_svc.create_book(actor=users["admin@example.com"], **spec)
            except DuplicateISBN:
                book = books_svc.books.get_by_isbn(spec["isbn"])
            books.append(book)
        db.commit()

        circ = CirculationService(db)
        librarian = users["librarian@example.com"]
        member = users["asha@example.com"]

        # One active loan
        try:
            circ.issue_book(books[0].id, member.id, actor=librarian)
        except Exception:
            pass
        db.commit()

        # One historical (returned) loan
        try:
            loan = circ.issue_book(books[2].id, users["ravi@example.com"].id, actor=librarian)
            db.commit()
            circ.return_book(loan.id, actor=librarian)
            db.commit()
        except Exception:
            pass

        print("Seed complete.")
        print("Demo accounts (email / password):")
        for _name, email, password, role in DEMO_USERS:
            print(f"  {role.value:<10} {email} / {password}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
