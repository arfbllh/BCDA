import json
from datetime import datetime

from core.config import get_config
from extensions import db
from models.analysis_job import AnalysisJob
from workers.celery_app import celery_app


def _run_llm_infer_job(job, payload):
    """Call optional OpenAI-compatible inference service; stub when not configured."""
    cfg = get_config()
    params = payload.get("parameters") or {}
    study_id = payload.get("study_id") or job.study_id
    prompt = (params.get("prompt") or "").strip() or (
        "Give a one-paragraph plain-language summary of key clinical and molecular "
        "dimensions researchers might explore in this study."
    )
    messages = [
        {"role": "system", "content": "You are a concise cancer genomics assistant."},
        {"role": "user", "content": f"Study id: {study_id}\n\n{prompt}"},
    ]

    if not cfg.LLM_INFERENCE_ENABLED or not (cfg.LLM_API_BASE_URL or "").strip():
        return {
            "job_id": job.job_id,
            "study_id": study_id,
            "job_type": job.job_type,
            "input": payload,
            "llm_mode": "stub",
            "assistant_message": (
                "LLM inference is not enabled. Set LLM_INFERENCE_ENABLED=true and "
                "LLM_API_BASE_URL to an OpenAI-compatible endpoint (e.g. Ollama / vLLM)."
            ),
            "processed_at": datetime.utcnow().isoformat(),
        }

    from services.llm_inference_client import chat_completion

    max_tok = params.get("max_tokens")
    if max_tok is not None:
        try:
            max_tok = int(max_tok)
        except (TypeError, ValueError):
            max_tok = None

    text = chat_completion(messages, max_tokens=max_tok)
    return {
        "job_id": job.job_id,
        "study_id": study_id,
        "job_type": job.job_type,
        "input": payload,
        "llm_mode": "live",
        "model": cfg.LLM_MODEL,
        "assistant_message": text,
        "processed_at": datetime.utcnow().isoformat(),
    }


@celery_app.task(name="workers.tasks.process_analysis_job")
def process_analysis_job(job_id):
    job = AnalysisJob.query.filter_by(job_id=job_id).first()
    if not job:
        return {"error": "job not found", "job_id": job_id}

    try:
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.session.commit()

        payload = {}
        if job.request_payload:
            payload = json.loads(job.request_payload)

        if job.job_type == "llm_infer":
            result = _run_llm_infer_job(job, payload)
        else:
            # Placeholder compute path for non-LLM analysis types.
            result = {
                "job_id": job.job_id,
                "study_id": job.study_id,
                "job_type": job.job_type,
                "input": payload,
                "summary": "Async analysis job completed successfully.",
                "processed_at": datetime.utcnow().isoformat(),
            }

        job.status = "completed"
        job.result_payload = json.dumps(result)
        job.error_message = None
        job.finished_at = datetime.utcnow()
        db.session.commit()
        return result
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = datetime.utcnow()
        db.session.commit()
        raise

