# Library Management System v5

A production-grade, modular Library Management Platform: FastAPI +
SQLAlchemy + PostgreSQL backend, React + TypeScript frontend, JWT auth
with role-based access control, a real circulation domain (issue/return/
renew/reserve/fines with enforced state machines), an explainable
recommendation engine, analytics, audit logging, and an AI librarian
built on a swappable provider abstraction.

This is a from-scratch architectural rebuild of an earlier CSV-backed
student project of the same name — see [CHANGELOG.md](CHANGELOG.md) for
exactly what changed and why.

## Features

- **Book catalog & copies** — books and their individual physical copies
  (accession number, location, condition) are modeled separately.
- **Circulation** — issue, return, renew (with a renewal cap), reserve,
  cancel reservation, automatic overdue detection, fine calculation on
  late return.
- **RBAC** — ADMIN / LIBRARIAN / MEMBER roles with an explicit,
  centralized permission map (`app/core/dependencies.py`).
- **JWT authentication** — bcrypt password hashing, access + refresh
  tokens, account-status enforcement on every request.
- **Analytics dashboard** — totals, utilization rate, most-borrowed
  books, category distribution, monthly circulation trend — rendered as
  live charts in the frontend.
- **Explainable recommendations** — deterministic signals (category/
  author history + popularity), each with a plain-language reason. No ML
  is used or claimed.
- **AI librarian** — provider-agnostic (`LLMProvider` protocol); ships
  with a dependency-free `MockProvider` by default and an optional
  Anthropic-backed provider.
- **Audit logging** — every meaningful mutation is recorded to an
  append-only `audit_logs` table.
- **REST API** — versioned under `/api/v1`, documented at `/swagger` and
  `/redoc`.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Auth | passlib/bcrypt, python-jose (JWT) |
| Database | PostgreSQL (production), SQLite (dev/tests) |
| Frontend | React 19, TypeScript, Vite, React Router, Recharts |
| Testing | pytest, pytest-cov, httpx (via FastAPI TestClient) |
| Quality | ruff, mypy, oxlint, tsc |
| Deployment | Docker, docker-compose, GitHub Actions |

## Project structure

```text
library-management-system-v5/
├── app/                # FastAPI backend
│   ├── core/            # config, security, logging, exceptions, RBAC deps
│   ├── api/v1/           # HTTP routes — thin, no business logic
│   ├── models/           # SQLAlchemy ORM models + state machines
│   ├── schemas/          # Pydantic request/response schemas
│   ├── repositories/     # Data access (SQLAlchemy)
│   ├── services/         # Business logic — the real "domain layer"
│   ├── ai/                # LLMProvider protocol + Mock/Anthropic providers
│   └── database/          # Session, Base, Alembic migrations
├── frontend/            # React + TypeScript + Vite SPA
├── tests/               # unit / api / integration pytest suites
├── scripts/             # seed_database.py, migrate_data.py, create_admin.py
├── docs/                # architecture, api, database, security, deployment, development
├── data/seed/            # copied legacy CSVs, used by migrate_data.py
├── Dockerfile, docker-compose.yml
└── .github/workflows/    # ci.yml, security.yml
```

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/swagger

## Quick start (local, no Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python scripts/seed_database.py     # demo accounts + books
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Demo accounts after seeding (see script output):
`admin@example.com` / `AdminPass123!` (also librarian@ and two member@ accounts).

## Database setup

Dev default is SQLite (zero setup). For PostgreSQL, set `DATABASE_URL`
in `.env` and run `alembic upgrade head`. See [docs/database.md](docs/database.md).

## Environment variables

See [.env.example](.env.example) for the full list with descriptions.

## API documentation

Full endpoint reference: [docs/api.md](docs/api.md). Interactive/auto-generated
docs at `/swagger` and `/redoc` once the server is running.

## Authentication

JWT access + refresh tokens; see [docs/security.md](docs/security.md) for
the full auth/authorization design.

## Testing

```bash
pytest -q --cov=app --cov-report=term-missing
```

**Verified in this environment: 25 passed, ~80% statement coverage.**
Covers unit tests for circulation state machines, the recommendation
engine, analytics, user management, and the AI mock provider; API tests
for auth and books; and one full end-to-end integration test that
exercises the exact workflow — create user → create book → create copy →
issue → verify unavailable → return → verify available.

## CI/CD

`.github/workflows/ci.yml` runs lint (ruff/oxlint), type checks
(mypy/tsc), the pytest suite, an Alembic migration smoke test, and a
frontend production build on every push/PR.
`.github/workflows/security.yml` runs `pip-audit` and `npm audit` on a
weekly schedule.

## Deployment

See [docs/deployment.md](docs/deployment.md) for Docker Compose and
bare-metal instructions.

## Data migration

`scripts/migrate_data.py` converts the legacy `books.csv` into the new
schema. Verified against this repository's actual data: **211/211 book
rows migrated, 0 rejected** (see [docs/database.md](docs/database.md) for
what is and isn't migrated, and why).

## AI architecture

See [docs/architecture.md](docs/architecture.md#ai-flow). Default
`AI_PROVIDER=mock` requires no API key. Set `AI_PROVIDER=anthropic` and
`AI_API_KEY` to use a real Claude model instead.

## Security

See [docs/security.md](docs/security.md) and [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap / known limitations

Honestly documented rather than glossed over — see the end of
[CHANGELOG.md](CHANGELOG.md):

- Token revocation/denylist not implemented (stateless JWT logout only).
- Rate limiting is a reverse-proxy responsibility, not in-process middleware.
- Legacy circulation history (`issued_books.csv`, `issue_log.txt`) is
  reported by the migration script but not fabricated into `Loan` rows.
- The frontend covers the core flows end-to-end but not every UI
  component listed in the original brief (e.g. a dedicated copy-management
  screen, per-role dashboard layouts) — these are natural next additions
  on top of a now-complete API.

## License

MIT — see [LICENSE](LICENSE).
