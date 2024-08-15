# Operations Runbook

## Purpose
Provide quick response playbooks for common incidents in the platform.

## Incident 1: Ingestion Run Failed
1. Check latest failed run in ingestion run table/API
2. Identify failing file and stage (`validate`, `transform`, `load`)
3. Inspect worker logs with request/run ID
4. Re-run ingestion for the failed file or full run after fix
5. Confirm row counts and data quality report

## Incident 2: Queue Backlog Growing
1. Check queue depth metric and worker concurrency
2. Verify worker health and restart stuck workers
3. Inspect long-running job types and timeout settings
4. Scale workers temporarily
5. Record root cause and add follow-up task

## Incident 3: API Latency Spike
1. Check p95 latency by endpoint in Grafana
2. Validate cache hit ratio and Redis health
3. Identify slow DB/parquet query and recent deploy changes
4. Apply mitigation (cache warmup, rollback, feature flag)
5. Add performance test for regression prevention

Related artifacts:
- `infra/monitoring/grafana/dashboards/bcancerportal-overview.json`
- `infra/monitoring/prometheus/alerts.yml`

## Incident 4: High API Error Rate
1. Check error class split (4xx vs 5xx)
2. Correlate with deployment time and specific endpoint
3. Confirm DB/Redis connectivity and resource limits
4. Roll back if systemic 5xx burst
5. Post-incident notes with prevention item

Related artifacts:
- `infra/monitoring/prometheus/alerts.yml`
- `infra/monitoring/prometheus/prometheus.yml`

## Incident 5: GPU Worker Unavailable (Optional Track)
1. Detect via inference failure and worker heartbeat metrics
2. Route jobs to fallback CPU/queue defer mode
3. Restart GPU worker and check CUDA/runtime health
4. Resume queued jobs and validate result integrity

## Standard Incident Template
- Incident ID
- Start/End time
- Impacted services
- User impact
- Root cause
- Immediate mitigation
- Permanent fix
- Follow-up owner and due date

## Monitoring Startup
1. Start API service first (must expose `:4000/metrics`).
2. Run monitoring stack:
   - `docker compose -f infra/docker/docker-compose.monitoring.yml up -d`
3. Access tools:
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3001` (admin/admin)
4. Confirm dashboard:
   - `BCancerPortal Core Platform Overview`
