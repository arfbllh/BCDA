import json
import uuid

from core.datetime_util import utc_now
from extensions import db
from models.analysis_job import AnalysisJob
from workers.tasks import process_analysis_job
from kombu.exceptions import OperationalError as KombuOperationalError


class AnalysisJobService:
    def create_job(self, study_id, job_type, payload):
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        job = AnalysisJob(
            job_id=job_id,
            study_id=study_id,
            job_type=job_type or "generic",
            status="queued",
            request_payload=json.dumps(payload or {}),
            queued_at=utc_now(),
        )
        db.session.add(job)
        db.session.commit()
        try:
            process_analysis_job.delay(job_id)
        except Exception as exc:
            # Local/dev fallback: if broker is unavailable, execute inline so jobs still work.
            if isinstance(exc, KombuOperationalError) or "Connection refused" in str(exc):
                process_analysis_job(job_id)
            else:
                raise
        return job

    def get_job(self, job_id):
        return AnalysisJob.query.filter_by(job_id=job_id).first()

