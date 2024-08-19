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

## Implementation (PR-20)
- Async jobs with `job_type: llm_infer` call an **OpenAI-compatible** HTTP endpoint (`LLM_API_BASE_URL`, e.g. Ollama `/v1`, vLLM, or OpenAI).
- When inference is disabled or the URL is unset, the worker returns a **stub** payload so local dev and CI stay deterministic.
- See `.env.example` and `infra/docker/docker-compose.llm.yml` (optional Ollama).
