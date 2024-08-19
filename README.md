# bcancerportal

A web application for exploring cancer genomics databases, built with Flask and React.js.

## Features

- Browse multiple cancer databases organized by cancer type
- View summary statistics and visualizations for each database
- Explore clinical patient data
- Analyze mutation profiles
- Examine gene expression, methylation, and protein data
- Interactive data visualization using Plotly and D3.js

## Project Structure

```
bcancerportalbd/
├── backend/              # Flask API, pipeline, workers (see backend/README.md)
│   ├── app.py            # Entrypoint
│   ├── core/             # Config, app factory helpers
│   ├── routes/           # REST resources
│   ├── requirements.txt  # Python dependencies
│   └── ...
├── frontend/             # React frontend
├── doc/                  # Architecture, ADRs, runbook
└── infra/                # Docker Compose (app, monitoring, Kafka, LLM)
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on pushes and pull requests to `main` / `master`: **Ruff** on `backend/`, **pytest** with the coverage gate in `pytest.ini`, **pip-audit** on `backend/requirements.txt`, and a **Docker** build of `backend/Dockerfile`. Configure branch protection to require these jobs before merge.

## Docker

Run the **API** (Gunicorn), **Celery worker**, **MySQL**, and **Redis** with Compose. Paths below are from the **repository root**.

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

Compose sets dev-oriented MySQL credentials (`root` / `rootpass`, database `cancer_db`). Override via environment variables or by editing `infra/docker/docker-compose.yml` for real deployments. Optional: set `SECRET_KEY` in the environment before `up` (see `.env.example`).

### Monitoring (Prometheus + Grafana)

The monitoring compose file attaches to the same Docker network as the app so Prometheus can scrape `api:4000`.

1. Start the app stack first (creates network `bcancerportal_net`).
2. Then:

```bash
docker compose -f infra/docker/docker-compose.monitoring.yml up -d
```

- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3001](http://localhost:3001) (default admin/admin in compose)

More detail: `doc/runbook.md`.

### Stop

```bash
docker compose -f infra/docker/docker-compose.yml down
docker compose -f infra/docker/docker-compose.monitoring.yml down
```

### Optional Kafka (ingestion events)

For **optional** ingestion lifecycle events (`ingestion.run.*`), start a local broker with `docker compose -f infra/docker/docker-compose.kafka.yml up -d`, set `KAFKA_ENABLED=true` and `KAFKA_BOOTSTRAP_SERVERS` (see `.env.example`), then run the ingestion pipeline. Topics default to `ingestion.events` and `ingestion.dlq`. Details: `doc/runbook.md`, `doc/adr/ADR-0008-kafka-ingestion-events.md`.

### Optional LLM inference (async jobs)

Submit `POST /api/v1/analysis/jobs` with `"job_type": "llm_infer"` and `parameters.prompt` (optional). When `LLM_INFERENCE_ENABLED` is false or `LLM_API_BASE_URL` is empty, the worker completes with a **stub** message. For a local GPU stack, use `docker compose -f infra/docker/docker-compose.llm.yml up -d`, pull a model with Ollama, then set `LLM_API_BASE_URL=http://localhost:11434/v1` and `LLM_MODEL` to that tag. See `doc/adr/ADR-0007-llm-service-boundary.md`.

## Setup Instructions

### Prerequisites

- Python 3.12+ (recommended; see `backend/Dockerfile`)
- Node.js 18+ (frontend)
- MySQL 8+ (or use `infra/docker/docker-compose.yml`)

### Backend Setup

1. Create a MySQL database (e.g. `cancer_db`).

2. Virtualenv and dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. Environment: copy `.env.example` to `.env` at the **repo root** (or under `backend/`). Values load from repo root first, then `backend/.env` (see `backend/core/config.py`).

4. Migrations (from `backend/`):

```bash
cd backend
export FLASK_APP=app.py
flask db upgrade
```

5. Run API:

```bash
python app.py
```

API: `http://localhost:4000`. Contract: `GET http://localhost:4000/api/v1/openapi.json`. More detail: `backend/README.md`.

### Frontend Setup

1. Install the required Node.js packages:

```bash
cd frontend
npm install
```

2. Start the React development server:

```bash
npm start
```

The React application will be available at http://localhost:3000.

## API

- **OpenAPI:** `GET /api/v1/openapi.json` (legacy alias: `/api/openapi.json`).
- **v1 base:** `/api/v1/...` (datasets, clinical, summary, analysis jobs, heatmap). Legacy paths under `/api/...` mirror the same resources for the existing frontend.

See `doc/api-contract.md` for the full contract draft.

## Technologies Used

### Backend
- Flask - Web framework
- SQLAlchemy - ORM for database interactions
- Pandas - Data manipulation
- Plotly - Data visualization
- PyMySQL - MySQL connector

### Frontend
- React - UI library
- React Router - Navigation
- React Bootstrap - UI components
- Axios - HTTP client
- Plotly.js - Interactive charts
- D3.js - Data visualization

## License

MIT