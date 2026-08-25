# Security

## Authentication

- Passwords are hashed with **bcrypt** (via `passlib`); plaintext
  passwords are never stored or logged.
- Login issues a short-lived **access JWT** (default 30 min) and a
  longer-lived **refresh JWT** (default 7 days), each signed with
  `JWT_SECRET` (HS256).
- Every protected route re-loads the user from the database on each
  request (`get_current_user`), so a disabled account is rejected
  immediately even with a still-valid token — token validity alone is
  not sufficient for access.

## Authorization (RBAC)

Permissions are centralized in one place: `ROLE_PERMISSIONS` in
`app/core/dependencies.py`, mapping `ADMIN` / `LIBRARIAN` / `MEMBER` to an
explicit permission set (`books:create`, `circulation:issue`,
`users:disable`, etc.). Routes declare the permission they need via
`Depends(require_permission("..."))`; no role checks are scattered inside
service or route bodies. To change what a role can do, edit one
dictionary.

## Secrets & configuration

- All secrets (`JWT_SECRET`, `DATABASE_URL`, `AI_API_KEY`) come from
  environment variables (`app/core/config.py`, backed by
  `pydantic-settings`) — never hardcoded, never committed. `.env` is
  gitignored; `.env.example` documents every variable with safe
  placeholder values.
- The legacy project's hardcoded default admin credentials have been
  removed entirely. `scripts/create_admin.py` is the only way to
  provision an admin, and it requires an explicit password of at least
  8 characters — there is no fallback default.

## CORS

`CORS_ORIGINS` (comma-separated) drives `CORSMiddleware`
(`app/main.py`) — no wildcard origin in the shipped configuration;
operators must explicitly list the frontend origin(s) allowed to call
the API.

## Input validation

Every request body is a Pydantic v2 schema (`app/schemas/`) with
explicit types, length constraints (e.g. `password: str =
Field(min_length=8)`), and `EmailStr` validation — invalid payloads are
rejected with `422` before reaching any service code.

## SQL injection

All database access goes through SQLAlchemy's ORM/Core query builder
(`app/repositories/`); there is no raw string-interpolated SQL anywhere
in the codebase.

## Error responses

`app/core/middleware.py` registers two handlers: one for typed
`AppError` subclasses (returns the mapped status code, a message, and an
`error_code` — see `app/core/exceptions.py`), and a catch-all for
anything unexpected, which logs the full traceback server-side but
returns a generic `500 INTERNAL_ERROR` to the client — internal stack
traces are never exposed over the API.

## Audit logging

Every meaningful state change — book created/updated/deleted, copy
added, book issued/returned/renewed, reservation created/cancelled, fine
paid, user created/role-changed/disabled, login/registration — is
recorded via `AuditService.record(...)` into the append-only
`audit_logs` table (actor, action, resource, resource_id, timestamp,
metadata). Nothing in the application ever updates or deletes an
existing audit row.

## Rate limiting

`RATE_LIMIT_PER_MINUTE` is exposed as a setting for a reverse-proxy or
gateway (e.g. nginx `limit_req`, or an API gateway) to enforce; it is not
implemented as in-process middleware in this codebase. **Documented
limitation** — see Roadmap in the README.

## Token revocation

JWTs are stateless; `/auth/logout` is a client-side no-op (discard the
tokens). A production deployment that needs immediate revocation (e.g.
"log this user out everywhere right now") would add a denylist keyed by
each token's `jti` claim (already present on every issued token), e.g. in
Redis with a TTL matching the token's remaining lifetime. **Documented
limitation**, not implemented in this version.

## Production deployment considerations

- Run behind TLS termination (reverse proxy / load balancer) — the app
  itself does not terminate HTTPS.
- Set `APP_ENV=production`, a strong random `JWT_SECRET`
  (`python -c "import secrets; print(secrets.token_urlsafe(48))"`), and
  a real `CORS_ORIGINS` list.
- Use PostgreSQL, not SQLite, in production (`docker-compose.yml` does
  this by default).
- Run `alembic upgrade head` before starting the app (the Compose `api`
  service's command does this automatically).
