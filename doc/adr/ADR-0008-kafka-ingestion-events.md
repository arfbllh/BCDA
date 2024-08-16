# ADR-0008 Optional Kafka for Ingestion Events

## Status
Accepted

## Context
Downstream systems (search indexes, audit, fan-out analytics) benefit from durable ingestion lifecycle events. The platform already uses Celery + Redis for job execution; Kafka is additive and must remain optional so local and CI environments stay simple.

## Decision
- Emit JSON events from the ingestion orchestrator when `KAFKA_ENABLED=true` and `KAFKA_BOOTSTRAP_SERVERS` is set.
- Topics: primary `ingestion.events`, dead-letter `ingestion.dlq` for publish failures.
- Use `kafka-python` with lazy producer initialization; no Kafka imports on the API hot path unless the pipeline runs.
- Ship a dev `docker-compose.kafka.yml` (KRaft) and a CLI consumer for debugging and consumer-group lag checks.

## Consequences
- Operators can monitor consumer lag and DLQ depth without changing core ingestion semantics.
- Extra dependency (`kafka-python`) and broker operations are opt-in; default configuration leaves Kafka off.
