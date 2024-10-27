# BCancerPortal

BCancerPortal is a full-stack web application for exploring breast-cancer study data through a React frontend and a Flask API.

## What this app does

The app helps teams browse studies, inspect clinical and genomic data, run analysis jobs, and monitor service health from one platform.

Core capabilities:

- Dataset/study browsing with API-backed pagination
- Clinical and summary endpoints for analytics views
- Heatmap and matrix-oriented data access
- Asynchronous analysis jobs with Celery workers
- Health/readiness/metrics endpoints for operations

## Who this app is for

BCancerPortal is designed for:

- Researchers and analysts working with breast-cancer study datasets
- Data/ML or bioinformatics teams that need pipeline-driven ingestion and query APIs
- Platform and engineering teams that want observability, background jobs, and deployment automation

---

## Architecture

High-level architecture:

- **Frontend (`frontend/`)**: React SPA that calls versioned REST APIs
- **Backend (`backend/`)**: Flask API with modular routes, services, repositories, and pipeline stages
- **Data layer**: MySQL for relational data and Parquet for matrix-style files
- **Async/queue layer**: Celery workers with Redis as broker/cache
- **Platform layer**: Docker Compose stacks, health checks, metrics, and optional Kafka/LLM integrations

Request flow (typical):

1. Client calls API (`/api/v1/...`)
2. API reads/writes MySQL and cache, and serves heavy matrix reads from Parquet when relevant
3. Long-running jobs are queued to Celery workers
4. Workers update job status/results and expose telemetry via metrics endpoints

---

## Features

- Browse studies/datasets by cancer type
- Summary dashboards (Plotly) and clinical tables (paginated API)
- Mutation and omics-oriented views; matrix data via pipeline/Parquet where applicable
- Async **analysis jobs** (e.g. survival, optional **`llm_infer`**)
- **Health** (`/healthz`), **readiness** (`/readyz`), **metrics** (`/metrics`)

---

## Project structure

Top-level structure:

```
bcancerportalbd/
├── backend/                 # Flask API, data pipeline, workers, tests
├── frontend/                # React single-page application
├── doc/                     # Architecture docs, runbooks, ADRs, API contract
├── infra/docker/            # Docker Compose stacks (app, monitoring, optional services)
└── .github/workflows/       # CI pipelines
```

Backend structure:

```
backend/
├── app.py
├── api/                     # OpenAPI, error envelope, v1 registration
├── core/                    # App config/factory and helpers
├── routes/                  # Flask REST resources
├── services/                # Business/domain logic
├── repositories/            # Data access patterns
├── pipeline/                # Ingestion stages and tracking
├── workers/                 # Celery app and async tasks
├── observability/           # Metrics/request context helpers
├── migrations/              # Alembic migrations
└── tests/
```

---

## CI

GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) on `main` / `master` and PRs: **Ruff** (`backend/`), **pytest** + coverage gate ([`pytest.ini`](pytest.ini)), **pip-audit** on [`backend/requirements.txt`](backend/requirements.txt), **Docker** build of [`backend/Dockerfile`](backend/Dockerfile). Use branch protection to require these checks before merge.

---

## How to run

You can run the project with Docker (recommended) or local development mode.

### Option A: Run with Docker (recommended)

Run **API** (Gunicorn), **Celery worker**, **MySQL**, and **Redis** with Compose. Commands below assume the **repository root**.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2

### Start the stack

```bash
docker compose -f infra/docker/docker-compose.yml up -d --build
```

Apply database migrations (first run and after migration changes):

```bash
docker compose -f infra/docker/docker-compose.yml exec api flask db upgrade
```

### URLs and defaults

- API: [http://localhost:4000](http://localhost:4000)
- Health: [http://localhost:4000/healthz](http://localhost:4000/healthz)
- Readiness (includes DB check): [http://localhost:4000/readyz](http://localhost:4000/readyz)
- Prometheus metrics: [http://localhost:4000/metrics](http://localhost:4000/metrics)

Compose uses dev-oriented MySQL credentials (`root` / `rootpass`, database `cancer_db`). Override via env or edit [`infra/docker/docker-compose.yml`](infra/docker/docker-compose.yml). Set `SECRET_KEY` before production use ([`.env.example`](.env.example)).

### Monitoring (Prometheus + Grafana)

The monitoring compose file joins the app network so Prometheus can scrape `api:4000`.

1. Start the app stack first (creates network `bcancerportal_net`).
2. Then:

```bash
docker compose -f infra/docker/docker-compose.monitoring.yml up -d
```

- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3001](http://localhost:3001) (default admin/admin in compose)

More detail: [`doc/runbook.md`](doc/runbook.md).

### Stop

```bash
docker compose -f infra/docker/docker-compose.yml down
docker compose -f infra/docker/docker-compose.monitoring.yml down
```

### Optional Kafka (ingestion events)

`docker compose -f infra/docker/docker-compose.kafka.yml up -d`, then `KAFKA_ENABLED=true` and `KAFKA_BOOTSTRAP_SERVERS` ([`.env.example`](.env.example)). Topics: `ingestion.events`, `ingestion.dlq`. See [`doc/runbook.md`](doc/runbook.md), [`doc/adr/ADR-0008-kafka-ingestion-events.md`](doc/adr/ADR-0008-kafka-ingestion-events.md).

### Optional LLM inference (async jobs)

`POST /api/v1/analysis/jobs` with `"job_type": "llm_infer"`. Stub response if LLM is not configured. Local stack: [`infra/docker/docker-compose.llm.yml`](infra/docker/docker-compose.llm.yml) (Ollama). See [`doc/adr/ADR-0007-llm-service-boundary.md`](doc/adr/ADR-0007-llm-service-boundary.md).

---

### Option B: Run locally (dev mode)

### Prerequisites

- Python **3.12+** (see [`backend/Dockerfile`](backend/Dockerfile))
- Node.js **18+** (frontend)
- **MySQL 8+** (or use app Compose stack)

### Backend

**Data plane (production-style):** The **catalog** (`GET /api/v1/datasets`) reads **MySQL `studies`**. **Clinical** and **summary** read **ingested** tables (`{study}_data_*`) produced by the **ingestion pipeline** (`python dataloader.py` from `backend/`, after placing bundles under **`DATASETS_BASE_DIR`** / default `backend/datasets` and a `datasets.csv` index). **Heatmap** and some **analysis** paths read **CSV files** from that same directory for the selected study (configurable via env). Large matrices can also be materialized to **Parquet** under **`MATRIX_STORAGE_DIR`** during ingestion.

1. **Create the MySQL database** (must exist before `flask db upgrade`). Names should match `MYSQL_DB` / `MYSQL_DB_TEST` in `.env` (defaults `cancer_db`, `cancer_db_test`):

   ```bash
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cancer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cancer_db_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

2. Virtualenv and install:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. Environment: copy [`.env.example`](.env.example) to `.env` at **repo root** (or `backend/.env`). Load order: repo root first, then `backend/` ([`backend/core/config.py`](backend/core/config.py)).

4. Migrations (from `backend/`; requires MySQL running and DB created in step 1):

```bash
cd backend
export FLASK_APP=app.py
flask db upgrade
```

5. Run API (from `backend/`):

```bash
cd backend
python app.py
```

- API: `http://localhost:4000`
- Contract: `GET /api/v1/openapi.json`
- Troubleshooting `/readyz`: [`backend/README.md`](backend/README.md)

### Frontend

```bash
cd frontend
npm install
npm start
```

App: [http://localhost:3000](http://localhost:3000).

---

## API

- **OpenAPI:** `GET /api/v1/openapi.json` (legacy: `/api/openapi.json`).
- **v1 base:** `/api/v1/...` (datasets, clinical, summary, analysis jobs, heatmap). Legacy `/api/...` mirrors the same resources for the current frontend.

Full contract draft: [`doc/api-contract.md`](doc/api-contract.md).

---

## Technology stack

### Backend

Flask, Flask-RESTful, SQLAlchemy, Flask-Migrate, Celery, Redis, PyMySQL, Pandas, Plotly, Pydantic, Prometheus client, optional `kafka-python`, stdlib HTTP for LLM client.

### Frontend

React, React Router, React Bootstrap, Axios, Plotly.js, D3.js.

---

## License

MIT
