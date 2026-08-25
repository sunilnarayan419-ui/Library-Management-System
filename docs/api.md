# API Reference

Base URL: `/api/v1`. Interactive docs: `/swagger` (Swagger UI) and
`/redoc` (ReDoc), auto-generated from the FastAPI route definitions —
always the authoritative, up-to-date reference. This document is a
human-readable summary.

All responses use the envelope:

```json
{ "success": true, "data": { ... }, "message": "..." }
```

Errors use the same shape with `"success": false` and an additional
`"error_code"` field (see `app/core/exceptions.py` for the full list).

## Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | none | Create an account (defaults to MEMBER role) |
| POST | `/auth/login` | none | Returns access + refresh JWTs |
| POST | `/auth/refresh` | none (refresh token in body) | Exchange refresh token for a new pair |
| POST | `/auth/logout` | Bearer | Stateless logout (client discards tokens) |
| GET | `/auth/me` | Bearer | Current user profile |

**Example — login:**
```bash
curl -X POST /api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "AdminPass123!"}'
```
Response `data`: `{ "user": {...}, "tokens": { "access_token": "...", "refresh_token": "...", "token_type": "bearer" } }`

All endpoints below require `Authorization: Bearer <access_token>` unless noted.

## Books — requires `books:view` / `books:create` / `books:update` / `books:delete`

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/books?search=&category=&page=&page_size=` | `books:view` | Paginated search |
| GET | `/books/{id}` | `books:view` | Single book with copy counts |
| POST | `/books` | `books:create` | Create book (+ optional `initial_copies`) |
| PATCH | `/books/{id}` | `books:update` | Partial update |
| DELETE | `/books/{id}` | `books:delete` | Fails (422) if any copy is not AVAILABLE |
| POST | `/books/{id}/copies` | `books:update` | Add a physical copy |

Error cases: `404 BOOK_NOT_FOUND`, `409 DUPLICATE_ISBN`, `422 VALIDATION_ERROR`.

## Users — requires `users:create` / `users:update` / `users:disable`

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/users?role=&page=&page_size=` | `users:create`* | List users |
| GET | `/users/{id}` | `users:create`* | Single user |
| POST | `/users` | `users:create` | Create user with a role |
| PATCH | `/users/{id}` | `users:update` | Change role and/or status |
| POST | `/users/{id}/disable` | `users:disable` | Shortcut to set status=DISABLED |

*Listing/reading users is gated on `users:create` (an admin-only permission
in the default role map) since only ADMIN needs the full user directory.

Error cases: `404 USER_NOT_FOUND`, `409 DUPLICATE_EMAIL`.

## Circulation — requires `circulation:issue` / `circulation:return` / `circulation:renew`

| Method | Path | Permission | Description |
|---|---|---|---|
| POST | `/circulation/issue` | `circulation:issue` | `{book_id, member_id, days?}` |
| POST | `/circulation/return` | `circulation:return` | `{loan_id}`; applies a fine if overdue |
| POST | `/circulation/renew` | `circulation:renew` | `{loan_id}`; blocked at `max_renewals` or if reserved by someone else |
| POST | `/reservations` | `circulation:issue` | `{book_id, member_id}`; only when no copies are available |
| DELETE | `/reservations/{id}` | `circulation:issue` | Cancel a pending reservation |
| POST | `/fines/{id}/pay` | `circulation:return` | Mark a fine as paid |

Error cases: `404 BOOK_NOT_FOUND` / `LOAN_NOT_FOUND` / `RESERVATION_NOT_FOUND`,
`409 BOOK_UNAVAILABLE` / `ALREADY_RETURNED` / `RENEWAL_NOT_ALLOWED`.

**Example — issue then return:**
```bash
curl -X POST /api/v1/circulation/issue -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"book_id": "...", "member_id": "..."}'

curl -X POST /api/v1/circulation/return -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"loan_id": "..."}'
```

## Analytics — requires `analytics:view`

| Method | Path | Description |
|---|---|---|
| GET | `/analytics/dashboard` | Totals: books, copies, overdue, active members, fines |
| GET | `/analytics/top-books` | Most borrowed titles |
| GET | `/analytics/categories` | Category distribution |
| GET | `/analytics/monthly-circulation` | Issued/returned per month, last 6 months |

## Recommendations — any authenticated user

| Method | Path | Description |
|---|---|---|
| GET | `/recommendations?member_id=&limit=` | Explainable picks for a member (defaults to caller) |

## AI — any authenticated user

| Method | Path | Description |
|---|---|---|
| POST | `/ai/chat` | `{message}` → catalog-grounded reply from the configured provider |

## Health

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | none | `{status, database, version}` |
