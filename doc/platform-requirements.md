# Platform Requirements

## Functional Requirements
- Ingest cBioPortal-style study bundles (`meta_*`, `data_*`, `case_lists/*`)
- Validate schema and required columns before load
- Support idempotent re-ingestion of the same study
- Expose REST endpoints for study metadata, summaries, and analyses
- Support async execution for long-running analyses
- Provide cache-backed responses for high-cost queries
- Track ingestion runs, status, row counts, and failures

## Non-Functional Requirements
- Availability target for API in local/prod-like setup
- P95 latency targets:
  - Cached endpoints: < 500ms
  - Uncached analytical endpoints: < 3s (excluding async jobs)
- Ingestion success rate target: > 99%
- Worker job success target: > 98%
- Horizontal scaling path for API and worker processes

## Data and Storage Requirements
- Clinical/metadata/mutations in relational DB
- Wide matrices (mRNA, methylation, linear CNA, RPPA) in Parquet partitions
- Object store for raw bundles and generated artifacts
- Retain checksum and provenance metadata for reproducibility

## Security Requirements
- All secrets via environment variables
- Dependency scanning in CI
- Input validation on all public API payloads
- API rate limiting and CORS policy hardening

## Observability Requirements
- `/healthz` and `/readyz` endpoints
- Prometheus metrics for request rate/errors/latency and queue depth
- Structured logs with request ID correlation
- Alert rules for worker failure, queue backlog, API error spike, DB latency

## Quality Requirements
- Unit tests for service and repository logic
- Integration tests for key API flows
- Pipeline tests for ingest stages with fixture data
- CI quality gate: lint + tests + coverage threshold

## Documentation Requirements
- Architecture blueprint
- API contract
- Data model reference
- Runbook for top incidents
- ADRs for major design choices
