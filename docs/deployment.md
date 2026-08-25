# Deployment

## Docker Compose (recommended)

```bash
cp .env.example .env   # edit JWT_SECRET etc.
docker compose up --build
```

This starts three services:

- `db` — PostgreSQL 16, with a healthcheck the `api` service waits on.
- `api` — runs `alembic upgrade head` then serves FastAPI via Gunicorn
  (4 Uvicorn workers) on port 8000.
- `frontend` — builds the React app and serves the static bundle via
  nginx on port 5173, proxying `/api/*` to the `api` service.

Visit `http://localhost:5173`. API docs at `http://localhost:8000/swagger`.

Bring it down (and drop the database volume) with:
```bash
docker compose down -v
```

## Bare-metal / VM

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL, JWT_SECRET, etc.
alembic upgrade head
python scripts/create_admin.py --email you@example.com --password '...' --name 'You'
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

Frontend:
```bash
cd frontend
npm ci
npm run build     # outputs frontend/dist — serve with any static host / nginx
```

## Environment variables

See `.env.example` for the full list. The ones that matter most in
production: `DATABASE_URL` (PostgreSQL), `JWT_SECRET` (strong random
value), `CORS_ORIGINS` (your real frontend origin), `APP_ENV=production`.

## Health checks

`GET /api/v1/health` returns `{"status", "database", "version"}` and is
suitable for a container orchestrator's liveness/readiness probe.

## Zero-downtime notes (roadmap)

This version runs a single `alembic upgrade head` before boot, which is
fine for the traffic levels described in the scalability target but is
not a rolling/blue-green migration strategy. For larger deployments,
migrations should be decoupled from app startup and run as a separate
release step. **Documented limitation**, not implemented in this version.
