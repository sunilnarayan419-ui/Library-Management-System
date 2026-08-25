# Database

## Engine

- **Production**: PostgreSQL (`DATABASE_URL=postgresql+psycopg2://...`)
- **Development/tests**: SQLite (`DATABASE_URL=sqlite:///./data/library.db`,
  or `sqlite:///:memory:` in the test suite)

SQLAlchemy 2.0 ORM (`app/models/`) is the only supported way to write to
the schema; the legacy project's CSV files are not read at runtime.

## Schema

| Table | Purpose |
|---|---|
| `users` | Accounts: name, email, password_hash, role, status, last_login_at |
| `books` | Catalog record: title, author, isbn, category, etc. |
| `book_copies` | One row per physical item; `status` enum (`AVAILABLE`, `ISSUED`, `RESERVED`, `LOST`, `DAMAGED`, `MAINTENANCE`) |
| `loans` | copy_id, book_id, member_id, issued_at, due_at, returned_at, renewal_count, status |
| `reservations` | book_id, member_id, status (`PENDING`, `FULFILLED`, `CANCELLED`, `EXPIRED`) |
| `fines` | loan_id, member_id, amount, status (`OUTSTANDING`, `PAID`, `WAIVED`) |
| `audit_logs` | Append-only: actor, action, resource, resource_id, timestamp, metadata_json |

Book vs. BookCopy is a deliberate 1-to-many split: a catalog entry
("Clean Code") can have several physical copies, each independently
trackable (accession number, shelf location, condition, current status).

## State machines

`app/models/book_copy.py` defines `ALLOWED_COPY_TRANSITIONS`, a table of
which `CopyStatus` values a copy may move to from its current status.
`CirculationService._transition_copy` is the single choke point that
enforces it — for example a copy cannot jump directly from `ISSUED` to
`RESERVED`; it must pass through `AVAILABLE` first, which is exactly what
`return_book` does.

`Loan.status` moves `ACTIVE → OVERDUE` (via `mark_overdue_loans`, an
idempotent sweep intended to run on a schedule) or `ACTIVE/OVERDUE →
RETURNED`.

## Migrations

Alembic is the source of truth for schema changes.

```bash
alembic revision --autogenerate -m "add xyz column"
alembic upgrade head
alembic downgrade -1
```

`app/main.py` also calls `Base.metadata.create_all()` on startup as a
SQLite/dev convenience so a fresh clone works without running migrations
first — in any environment where `alembic upgrade head` has been run,
this is a no-op (tables already match).

## Data migration from v4 (CSV)

`scripts/migrate_data.py` reads the legacy `books.csv`
(`Title,Author,Subject,Extent,Publisher`) and inserts one `Book` +
one `BookCopy` per row (matching the legacy "one row = one physical
item" model), validating that `Title` is non-empty and skipping/reporting
rows that aren't. It does **not** attempt to convert
`issued_books.csv`/`issue_log.txt` into `Loan` rows: those files only
contain free-text lender names (no email/password), so there's no way to
attach that history to a real account without fabricating data. The
script counts and reports these files in `migration_report.json` instead
of silently discarding them — see the script's docstring for the full
rationale. Verified: running it against this repository's actual
`books.csv` (211 data rows) inserted 211 books with 0 rejections.

## Indexes

`email` (users), `isbn`/`title`/`author`/`category` (books),
`accession_number` (book_copies), and the various foreign keys are all
indexed via `index=True` / `unique=True` on the relevant `mapped_column`
declarations, so lookups and the paginated `/books` search stay
efficient as the catalog grows.
