# Contributing

Thanks for considering a contribution to the Library Management System.

## Getting set up

See `docs/development.md` for the full local setup (backend + frontend +
tests + linting).

## Workflow

1. Fork/branch from `main`.
2. Make your change. Keep business logic in `app/services/`, not in
   route handlers — see `docs/architecture.md` for the layering rules.
3. Add or update tests. New service methods should have unit tests
   (`tests/unit/`); new endpoints should have at least one API test
   (`tests/api/`).
4. Run the full check locally before opening a PR:
   ```bash
   ruff check app tests scripts
   mypy app
   pytest -q --cov=app
   cd frontend && npm run lint && npm run typecheck && npm run build
   ```
5. If you changed the database schema, generate a migration:
   ```bash
   alembic revision --autogenerate -m "describe the change"
   ```
   and commit it alongside your model change.
6. Open a PR describing what changed and why. CI (`.github/workflows/ci.yml`)
   must pass.

## Code style

- Python: `ruff` (lint) + `mypy` (types) + type hints throughout;
  avoid `Any` where a real type is available.
- TypeScript: strict mode is on (`frontend/tsconfig.json`); avoid `any`.
- Keep services single-responsibility. If a service method is doing two
  unrelated things, it's a sign to split it.

## Reporting bugs / requesting features

Open an issue with steps to reproduce (for bugs) or a clear description
of the use case (for features). For security issues, see `SECURITY.md`
instead of a public issue.
