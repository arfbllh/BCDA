# Backend (BCancerPortal)

Flask app factory, REST API (`/api/v1/...` and legacy `/api/...`), SQLAlchemy + migrations, Celery workers, ingestion pipeline, optional Redis cache / Kafka / LLM.

## Quick start (local)

1. Python **3.12+** recommended (matches `Dockerfile`).
2. Create a virtualenv and install deps:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy env template from repo root: `cp ../.env.example ../.env` (or `cp .env.example .env` if you keep `.env` under `backend/`). Variables are loaded from **repository root** `.env` first, then **`backend/.env`**. Set `MYSQL_DB` (default `cancer_db`) and credentials to match your server.

4. **Create the database** (once per machine). Flask-Alembic connects to the DB named in `MYSQL_DB`; MySQL returns *Unknown database* if it does not exist yet. From a shell (adjust user/password/host to match `.env`):

   ```bash
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cancer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

   For pytest, create the test DB too (see `MYSQL_DB_TEST` in `.env.example`), e.g. `cancer_db_test`.

5. Run migrations from `backend/`:

   ```bash
   export FLASK_APP=app.py
   flask db upgrade
   ```

6. Run API:

   ```bash
   python app.py
   ```

   Served at `http://127.0.0.1:4000`. OpenAPI: `GET /api/v1/openapi.json`.

7. Tests (from repository root):

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

## Troubleshooting `/readyz`

`/readyz` returns **503** when **`checks.db`** is false: the app cannot run `SELECT 1` against MySQL using `SQLALCHEMY_DATABASE_URI`.

1. **MySQL running?** `mysqladmin ping` or your Docker healthcheck.
2. **Database exists?** `CREATE DATABASE cancer_db;` (or whatever `MYSQL_DB` is).
3. **Credentials / host / port** match `.env` (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`).
4. **Migrations applied?** From `backend/`: `export FLASK_APP=app.py && flask db upgrade`.
5. **Docker stack:** `docker compose -f ../infra/docker/docker-compose.yml up -d`, then `docker compose ... exec api flask db upgrade`.

`/healthz` staying **200** while `/readyz` is **503** is normal: the process is up but the data plane is not ready yet.

## Conventions (readability)

- **Layers:** routes thin → services orchestrate → repositories / raw SQL for reads where ORM is not used.
- **Config:** `core.config` + env vars; avoid magic strings for feature flags.
- **Comments:** explain *why* and non-obvious invariants (e.g. SQL identifier rules, cache namespace bumps), not what the next line obviously does.
- **Errors:** API validation and standard error envelope via `api.error_response.api_error`.
