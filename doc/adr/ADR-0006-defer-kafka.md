# ADR-0006 Defer Kafka Until Needed

## Status
Accepted

## Context
Current scope can be served by queue-based async jobs; full event streaming is not mandatory at initial stage.

## Decision
Start with Celery + Redis. Introduce Kafka in a later optional PR for streaming ingestion and replay semantics.

## Consequences
- Reduces early complexity
- Keeps a clear growth path for high-throughput event ingestion narrative
