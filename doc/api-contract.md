# API Contract (v1 Draft)

Base path: `/api/v1`

## Studies
- `GET /studies`
  - List available studies with basic metadata
- `GET /studies/{studyId}`
  - Study detail, counts, and ingestion status

## Ingestion
- `POST /ingestion/runs`
  - Trigger ingestion for a study bundle
  - Request: `{ "study_id": "brca_tcga_pub2015", "source_path": "..." }`
  - Response: `{ "run_id": "...", "status": "queued" }`
- `GET /ingestion/runs/{runId}`
  - Ingestion run status and per-stage progress
- `GET /ingestion/runs/{runId}/report`
  - Data quality and load report

## Clinical and Summary
- `GET /studies/{studyId}/summary`
  - Summary metrics and distributions for dashboard widgets
- `GET /studies/{studyId}/clinical`
  - Paginated clinical records with filters

Implemented mirror (legacy path also under `/api/datasets/...`):
- `GET /api/v1/datasets/{dataset_name}/clinical?limit=&offset=`
  - `limit` is capped by `API_MAX_CLINICAL_ROWS` (default 500); defaults to `API_CLINICAL_DEFAULT_LIMIT` (200).
  - Response: `{ "items": [...], "total": <row count>, "limit": <n>, "offset": <n> }`.

## Analysis
- `POST /analysis/jobs`
  - Submit async analysis (`survival`, `correlation`, `llm_infer`, etc.). For `llm_infer`, pass `parameters.prompt` (optional); requires `LLM_INFERENCE_ENABLED` and OpenAI-compatible `LLM_API_BASE_URL`, else the worker returns a stub payload.
- `GET /analysis/jobs/{jobId}`
  - Job status and metadata
- `GET /analysis/jobs/{jobId}/result`
  - Final result payload

## Gene/Matrix Query
- `GET /studies/{studyId}/genes/{geneSymbol}/mutation-frequency`
- `GET /studies/{studyId}/genes/{geneSymbol}/expression`
- `GET /studies/{studyId}/genes/{geneSymbol}/methylation`

## Platform
- `GET /healthz`
- `GET /readyz`
- `GET /metrics` (Prometheus scrape endpoint)

## Error Contract (Standard)
All non-2xx responses return:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "request_id": "string"
  }
}
```

## Versioning Rules
- Breaking changes create `/api/v2`
- Additive changes remain in `/api/v1`
