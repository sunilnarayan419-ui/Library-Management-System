#!/usr/bin/env python
"""Migrate legacy CSV/text data (books.csv, issued_books.csv, issue_log.txt)
from the v4 CLI/Flask-adapter project into the v5 relational schema.

What it does:
    1. Parses books.csv (Title,Author,Subject,Extent,Publisher) into Book +
       BookCopy records (one copy per catalog row, matching legacy behaviour
       of "one row = one physical item").
    2. Validates each row; rejects rows with an empty title.
    3. Reports historical circulation data found in issued_books.csv /
       issue_log.txt for operator awareness, but does NOT fabricate Loan
       records for it: the legacy files only contain free-text lender
       names, not accounts with emails/passwords, so there is no safe way
       to attach that history to a real User in the new schema without
       inventing data. This is a deliberate, documented limitation — see
       the printed summary and docs/database.md — not a silent data loss.
    4. Writes a migration_report.json summarising what was inserted,
       skipped, and why.

Usage:
    python scripts/migrate_data.py --books-csv path/to/books.csv \
        --issued-csv path/to/issued_books.csv --log-file path/to/issue_log.txt
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.core.exceptions import DuplicateISBN, ValidationError
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.services.book_service import BookService


def parse_books_csv(path: Path) -> tuple[list[dict], list[dict]]:
    accepted: list[dict] = []
    rejected: list[dict] = []
    if not path.exists():
        return accepted, rejected

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            title = (row.get("Title") or "").strip()
            author = (row.get("Author") or "").strip()
            if not title:
                rejected.append({"row": i, "reason": "empty title", "raw": row})
                continue
            accepted.append(
                {
                    "title": title,
                    "author": author or "Unknown",
                    "category": (row.get("Subject") or "").strip() or None,
                    "publisher": (row.get("Publisher") or "").strip() or None,
                }
            )
    return accepted, rejected


def count_legacy_circulation_events(issued_csv: Path, log_file: Path) -> dict:
    issued_rows = 0
    if issued_csv.exists():
        with issued_csv.open(encoding="utf-8") as f:
            issued_rows = sum(1 for _ in f)
    log_lines = 0
    if log_file.exists():
        with log_file.open(encoding="utf-8") as f:
            log_lines = sum(1 for _ in f)
    return {"issued_books_csv_rows": issued_rows, "issue_log_lines": log_lines}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--books-csv", default="data/seed/books.csv")
    parser.add_argument("--issued-csv", default="data/seed/issued_books.csv")
    parser.add_argument("--log-file", default="data/seed/issue_log.txt")
    parser.add_argument("--report", default="migration_report.json")
    args = parser.parse_args()

    books_csv = Path(args.books_csv)
    accepted, rejected = parse_books_csv(books_csv)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted = 0
    duplicates = []
    try:
        service = BookService(db)
        for record in accepted:
            try:
                service.create_book(
                    title=record["title"],
                    author=record["author"],
                    category=record["category"],
                    publisher=record["publisher"],
                    initial_copies=1,
                )
                inserted += 1
            except (DuplicateISBN, ValidationError) as exc:
                duplicates.append({"title": record["title"], "reason": str(exc)})
        db.commit()
    finally:
        db.close()

    circulation_info = count_legacy_circulation_events(Path(args.issued_csv), Path(args.log_file))

    report = {
        "source_books_csv": str(books_csv),
        "rows_read": len(accepted) + len(rejected),
        "books_inserted": inserted,
        "rows_rejected": rejected,
        "duplicate_or_invalid_on_insert": duplicates,
        "legacy_circulation_data_found": circulation_info,
        "circulation_migration_note": (
            "Legacy issued_books.csv / issue_log.txt entries were counted but not "
            "converted into Loan records: they contain free-text lender names with "
            "no email/password, so there is no safe, non-fabricated way to map them "
            "to accounts in the new schema. Review these files manually if historical "
            "loan records must be preserved."
        ),
    }

    Path(args.report).write_text(json.dumps(report, indent=2))
    print(f"Migrated {inserted} books from {books_csv} ({len(rejected)} rows rejected).")
    print(f"Full report written to {args.report}")


if __name__ == "__main__":
    main()
