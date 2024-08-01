import json
from datetime import datetime

from extensions import db
from models.analysis_job import AnalysisJob
from workers.celery_app import celery_app


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

        # Placeholder compute path; replaced by real analysis engines in later PRs.
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

