# Changelog

## v5.0.0 — Modular production architecture

Complete architectural modernization from the v4.x legacy codebase.

### v4.x → v5.0.0: what changed

| | v4.x (legacy) | v5.0.0 |
|---|---|---|
| Backend | Flask, single `server.py` acting as an AST-based adapter around a `main.py` CLI class | FastAPI, layered `app/{api,services,repositories,models}` |
| Persistence | `books.csv`, `issued_books.csv`, `issue_log.txt` | PostgreSQL (SQLite for dev/tests) via SQLAlchemy 2.0 + Alembic |
| Auth | Hardcoded default passwords, header-based role flags | bcrypt password hashing, JWT access/refresh tokens |
| Authorization | Ad hoc checks | Centralized `ROLE_PERMISSIONS` map + `require_permission()` dependency |
| Circulation | Global in-memory list mutated directly by route handlers | `CirculationService` with explicit `BookCopy`/`Loan`/`Reservation` state machines, transactional issue/return/renew/reserve |
| Books vs. copies | One row per "book" as an issuable unit | Explicit `Book` (catalog) / `BookCopy` (physical item) split |
| AI librarian | Inline keyword dictionary inside `server.py` | `LLMProvider` protocol; `MockProvider` (generalizes the same keyword logic, zero dependencies) + optional `AnthropicProvider` |
| Recommendations | Not present | `RecommendationService`: deterministic, explainable, category/author/popularity signals |
| Analytics | `library_report.txt` static dump | `AnalyticsService` + `/analytics/*` endpoints + live dashboard charts |
| Audit trail | `issue_log.txt` free text | Structured, append-only `audit_logs` table |
| API | A handful of ad hoc Flask routes | Versioned REST API under `/api/v1`, OpenAPI docs at `/swagger` and `/redoc` |
| Frontend | Single `app.jsx` loaded via CDN script tag, no build step | React + TypeScript + Vite SPA with routing, protected routes, and role-aware navigation |
| Tests | None | pytest suite: unit, API, and full-workflow integration tests |
| Deployment | Procfile (Heroku-style) | Dockerfile + docker-compose (Postgres + API + frontend), GitHub Actions CI |
| Data migration | N/A | `scripts/migrate_data.py`, verified against this repo's actual `books.csv` (211/211 rows migrated) |

### Known limitations carried into v5.0.0

- Token revocation is not implemented (stateless JWT `/logout` is
  client-side only) — see `docs/security.md`.
- Rate limiting is exposed as a setting for a reverse proxy to enforce,
  not implemented as in-process middleware.
- Historical circulation data in the legacy `issued_books.csv` /
  `issue_log.txt` is reported by the migration script but intentionally
  **not** converted into `Loan` rows, since those files only contain
  free-text names with no account to attach the history to.
- The frontend implements the core flows (auth, book catalog + search,
  circulation, dashboard analytics with charts, recommendations, AI
  chat, user management) rather than every component/page listed in the
  original modernization brief (e.g. dedicated per-role dashboard
  layouts, full copy-management UI, reservation/fine management UI).
  These are natural fast-follow additions on top of the now-complete API.
