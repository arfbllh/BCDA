import json

from core.config import get_config
from core.datetime_util import utc_now, utc_now_iso
from extensions import db
from models.analysis_job import AnalysisJob
from models.upload_submission import UploadSubmission
from services.upload_service import UploadService
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
            "processed_at": utc_now_iso(),
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
        "processed_at": utc_now_iso(),
    }


@celery_app.task(name="workers.tasks.process_analysis_job")
def process_analysis_job(job_id):
    job = AnalysisJob.query.filter_by(job_id=job_id).first()
    if not job:
        return {"error": "job not found", "job_id": job_id}

    try:
        job.status = "running"
        job.started_at = utc_now()
        db.session.commit()

        payload = {}
        if job.request_payload:
            payload = json.loads(job.request_payload)

        if job.job_type == "llm_infer":
            result = _run_llm_infer_job(job, payload)
        elif job.job_type == "ml_risk":
            vals = payload.get("parameters", {}).get("values") or [1, 2, 3, 4, 5]
            vals = [float(v) for v in vals]
            cutoff = sorted(vals)[max(0, int(len(vals) * 0.7) - 1)]
            result = {
                "job_id": job.job_id,
                "study_id": job.study_id,
                "job_type": job.job_type,
                "risk_cutoff": cutoff,
                "high_risk_count": len([v for v in vals if v >= cutoff]),
                "low_risk_count": len([v for v in vals if v < cutoff]),
                "processed_at": utc_now_iso(),
            }
        elif job.job_type == "ml_feature":
            pairs = payload.get("parameters", {}).get("pairs") or []
            scored = [
                {"feature": p.get("feature"), "importance": abs(float(p.get("score", 0.0)))}
                for p in pairs
                if p.get("feature")
            ]
            scored.sort(key=lambda r: r["importance"], reverse=True)
            result = {
                "job_id": job.job_id,
                "study_id": job.study_id,
                "job_type": job.job_type,
                "top_features": scored[:20],
                "processed_at": utc_now_iso(),
            }
        elif job.job_type == "ml_baseline":
            metrics = payload.get("parameters", {}).get("metrics") or {}
            auc = float(metrics.get("auc", 0.72))
            f1 = float(metrics.get("f1", 0.68))
            result = {
                "job_id": job.job_id,
                "study_id": job.study_id,
                "job_type": job.job_type,
                "model": "baseline_logistic",
                "metrics": {
                    "auc": auc,
                    "f1": f1,
                    "confusion_matrix": metrics.get("confusion_matrix", [[42, 8], [11, 39]]),
                },
                "processed_at": utc_now_iso(),
            }
        else:
            # Placeholder compute path for non-LLM analysis types.
            result = {
                "job_id": job.job_id,
                "study_id": job.study_id,
                "job_type": job.job_type,
                "input": payload,
                "summary": "Async analysis job completed successfully.",
                "processed_at": utc_now_iso(),
            }

        job.status = "completed"
        job.result_payload = json.dumps(result)
        job.error_message = None
        job.finished_at = utc_now()
        db.session.commit()
        return result
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = utc_now()
        db.session.commit()
        raise


@celery_app.task(name="workers.tasks.process_upload_ingestion")
def process_upload_ingestion(upload_id):
    row = UploadSubmission.query.filter_by(upload_id=upload_id).first()
    if row is None:
        return {"error": "upload not found", "upload_id": upload_id}
    service = UploadService()
    service.run_ingestion_for_upload(row)
    return {"upload_id": upload_id, "status": row.status, "study_id": row.study_id}

