# Backend (BCancerPortal)

Flask app factory, REST API (`/api/v1/...` and legacy `/api/...`), SQLAlchemy + migrations, Celery workers, ingestion pipeline, optional Redis cache / Kafka / LLM.

## Quick start (local)

1. Python **3.12+** recommended (matches `Dockerfile`).
2. Create a virtualenv and install deps:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy env template from repo root: `cp ../.env.example ../.env` (or `cp .env.example .env` if you keep `.env` under `backend/`). Variables are loaded from **repository root** `.env` first, then **`backend/.env`**.
4. Ensure MySQL is running and the database exists; run migrations from `backend/`:

   ```bash
   export FLASK_APP=app.py
   flask db upgrade
   ```

5. Run API:

   ```bash
   python app.py
   ```

   Served at `http://127.0.0.1:4000`. OpenAPI: `GET /api/v1/openapi.json`.

6. Tests (from repository root):

   ```bash
   pytest
   ```

## Layout (high level)

| Path | Role |
|------|------|
| `core/` | Config, app factory helpers, pagination |
| `api/` | OpenAPI spec, error envelope, v1 registration |
| `routes/` | Flask-RESTful resources |
| `services/`, `repositories/` | Domain logic and DB access |
| `pipeline/` | Ingestion stages and run tracking |
| `workers/` | Celery app and tasks |
| `events/` | Optional Kafka ingestion producer |
| `observability/` | Metrics, request IDs |
| `migrations/` | Alembic revisions |
| `tests/` | Pytest |

Full architecture notes: `../doc/core-platform-architecture.md`.

## Workers

- Celery worker (from `backend/`): `celery -A celery_worker.celery_app worker --loglevel=info`
- Requires Redis (or set `CELERY_TASK_ALWAYS_EAGER=true` for dev-only in-process execution).
