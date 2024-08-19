# Interview Walkthrough Script

## Elevator Pitch
I built a cBioPortal-inspired breast cancer genomics platform using Flask REST APIs, asynchronous data pipelines, split analytical storage, and SRE-grade delivery and observability practices.

## Section 1: Code and Architecture Walkthrough
- Show backend structure and explain thin `app.py`
- Walk through one end-to-end flow:
  - study ingestion request
  - queue execution
  - data loaded to SQL + Parquet
  - summary API response with cache and metrics
- Explain key tradeoffs:
  - Flask retained for speed and continuity
  - split storage for matrix performance
  - async jobs for heavy analysis

## Section 2: How I Work
Use 1-2 concrete examples:
- PR example: feature decomposition, tests added, review feedback handled
- Incident/debug example: metric alert, root cause analysis, fix, verification

## Evidence Checklist
- One architecture diagram
- One merged PR with clear scope and test output
- One CI pipeline run screenshot
- One dashboard panel screenshot
- One short incident timeline note

## Suggested Demo Order (10-15 min)
1. Problem and scope (1 min)
2. Architecture diagram (2 min)
3. Code navigation and boundaries (4 min)
4. Pipeline and observability proof (3 min)
5. Workflow and PR/process proof (3 min)
6. Future scaling path (1 min)
   - Optional: Kafka ingestion fan-out; optional LLM job type (`llm_infer`) behind an OpenAI-compatible GPU/edge endpoint (Ollama/vLLM) with stub fallback when disabled
