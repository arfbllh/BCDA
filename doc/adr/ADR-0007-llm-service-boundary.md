# ADR-0007 LLM Inference as Separate Service

## Status
Accepted

## Context
GPU-backed inference has different runtime, scaling, and failure patterns from core API services.

## Decision
Keep LLM inference in a separate service behind async job orchestration.

## Consequences
- Isolates failures and allows independent scaling
- Adds deployment and observability complexity for AI path
