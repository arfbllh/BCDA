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
1. Start the app stack (creates Docker network `bcancerportal_net` and service `api` on port 4000):
   - `docker compose -f infra/docker/docker-compose.yml up -d`
   - Apply DB migrations if needed: `docker compose -f infra/docker/docker-compose.yml exec api flask db upgrade`
2. Run monitoring stack (joins the same network so Prometheus can scrape `api:4000`):
   - `docker compose -f infra/docker/docker-compose.monitoring.yml up -d`
3. Access tools:
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3001` (admin/admin)
4. Confirm dashboard:
   - `BCancerPortal Core Platform Overview`

## Optional Kafka (ingestion events)
1. Start broker: `docker compose -f infra/docker/docker-compose.kafka.yml up -d`
2. Create topics `ingestion.events` and `ingestion.dlq` (see comments in that compose file).
3. Set `KAFKA_ENABLED=true` and `KAFKA_BOOTSTRAP_SERVERS` (e.g. `localhost:9092`) for the process running `dataloader` / orchestrator.
4. **Lag**: use your cluster’s `kafka-consumer-groups.sh --describe` (or UI) with group `bcancerportal-ingestion-monitor` when running `python -m events.ingestion_consumer_cli` from `backend/` with `PYTHONPATH` set.
5. **Dead letter**: inspect `ingestion.dlq` for failed deliveries (`event_type: ingestion.delivery_failed`).

Related: `doc/adr/ADR-0008-kafka-ingestion-events.md`.

## Incident 6: Ingestion Events Not Appearing (Kafka)
1. Confirm `KAFKA_ENABLED` and broker reachability from the ingestion host
2. Verify topics exist and ACLs allow the producer client id
3. Check pipeline logs for “Kafka producer initialization failed” or publish errors
4. Drain `ingestion.dlq` and replay or fix broker/topic issues
5. Re-run ingestion for affected studies after recovery
