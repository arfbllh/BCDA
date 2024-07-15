# ADR-0003 Use Celery and Redis for Async Jobs

## Status
Accepted

## Context
Ingestion and analytical requests can be long-running and should not block API threads.

## Decision
Use Celery workers with Redis broker/backing store for asynchronous tasks and status tracking.

## Consequences
- Improves API responsiveness and reliability under load
- Adds queue operational overhead and worker lifecycle management
- Establishes foundation for future GPU inference jobs
