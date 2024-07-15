# ADR-0001 Keep Flask and Adopt App Factory

## Status
Accepted

## Context
Current backend is Flask with most wiring and logic concentrated in `backend/app.py` and route modules.

## Decision
Keep Flask and move to app factory + blueprint architecture.

## Consequences
- Lower migration risk than framework replacement
- Faster incremental delivery for PR-by-PR roadmap
- Requires disciplined modular boundaries to avoid monolithic route files
