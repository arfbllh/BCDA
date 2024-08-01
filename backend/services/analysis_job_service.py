import json
import uuid
from datetime import datetime

from extensions import db
from models.analysis_job import AnalysisJob
from workers.tasks import process_analysis_job


class AnalysisJobService:
    def create_job(self, study_id, job_type, payload):
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        job = AnalysisJob(
            job_id=job_id,
            study_id=study_id,
            job_type=job_type or "generic",
            status="queued",
            request_payload=json.dumps(payload or {}),
            queued_at=datetime.utcnow(),
        )
        db.session.add(job)
        db.session.commit()
        process_analysis_job.delay(job_id)
        return job

    def get_job(self, job_id):
        return AnalysisJob.query.filter_by(job_id=job_id).first()

