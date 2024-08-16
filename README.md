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
cancer-db-explorer/
├── backend/              # Flask backend
│   ├── app.py            # Main Flask application
│   ├── models.py         # Database models
│   ├── database.py       # Database connection
│   ├── config.py         # Configuration
│   └── routes/           # API endpoints
├── frontend/             # React frontend
│   ├── public/           # Static files
│   └── src/              # React source code
└── requirements.txt      # Python dependencies
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

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### Backend Setup

1. Create a MySQL database:

```sql
CREATE DATABASE cancer_db;
```

2. Set up a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Configure your database connection in `backend/config.py` or use environment variables:

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=yourusername
export MYSQL_PASSWORD=yourpassword
export MYSQL_DB=cancer_db
```

5. Run the Flask backend:

```bash
cd backend
python app.py
```

The Flask API will be available at http://localhost:4000.

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

## API Endpoints

### Database Endpoints

- `GET /api/databases/` - Get all databases grouped by type
- `GET /api/databases/:database_name` - Get information about a specific database
- `GET /api/databases/tables/:database_name` - Get all tables for a specific database

### Data Endpoints

- `GET /api/data/summary/:database_name` - Get summary statistics and graphs for a database
- `GET /api/data/clinical/:database_name` - Get clinical data for a database
- `GET /api/data/mutations/:database_name` - Get mutation data for a database

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