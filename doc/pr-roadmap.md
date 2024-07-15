# PR Roadmap (Execution Plan)

## PR-01 Documentation Foundation
Create all docs in `doc/` to lock architecture, requirements, API contract, runbook, ADRs, and interview narrative.

## PR-02 Flask App Factory
Introduce `create_app()` and make `backend/app.py` wiring-only.

## PR-03 Modular Backend Layout
Create `core`, `api/v1`, `services`, `repositories`, `pipeline`, `workers`, `observability` packages.

## PR-04 Config Hardening
Environment-based config classes, `.env.example`, and secret handling rules.

## PR-05 Data Model + Migrations
Set up Flask-Migrate/Alembic and add core relational tables.

## PR-06 Pipeline Extraction
Refactor current loader into staged pipeline modules with explicit interfaces.

## PR-07 Idempotent Ingestion
Checksum-based run dedupe, resumability, and per-file error isolation.

## PR-08 Matrix Storage Split
Persist wide matrices as Parquet partitions and read via DuckDB/PyArrow.

## PR-09 Async Jobs
Add Celery workers for heavy analyses and job status endpoints.

## PR-10 Redis Cache Layer
Cache expensive summary and analysis responses with invalidation strategy.

## PR-11 Request/Response Schemas
Add schema validation and publish OpenAPI docs.

## PR-12 Automated Testing
Add unit/integration/pipeline tests with fixture data and coverage gate.

## PR-13 Data Quality Checks
Implement schema drift, null-rate, and consistency checks.

## PR-14 Observability Baseline
Metrics, request IDs, structured logs, `/healthz`, `/readyz`.

## PR-15 Dashboards and Alerts
Provision Grafana dashboards and alert rules with runbook links.

## PR-16 Containerization
Dockerize API/worker and provide full `docker-compose` stack.

## PR-17 CI/CD
GitHub Actions for lint, test, security scan, build, and deploy gates.

## PR-18 Performance Pass
Query optimization, pagination, and throughput tuning.

## PR-19 Optional Kafka Stream
Event-driven ingestion updates with lag and dead-letter monitoring.

## PR-20 Optional LLM + GPU
Async inference service integration and final interview polish.
