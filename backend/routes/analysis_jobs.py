import json

from flask import request
from flask_restful import Resource

from services.analysis_job_service import AnalysisJobService


class AnalysisJobs(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def post(self):
        payload = request.get_json(silent=True) or {}
        study_id = payload.get("study_id", "unknown_study")
        job_type = payload.get("job_type", "generic")
        job = self.service.create_job(study_id=study_id, job_type=job_type, payload=payload)
        return {
            "job_id": job.job_id,
            "status": job.status,
            "study_id": job.study_id,
            "job_type": job.job_type,
        }, 202


class AnalysisJobStatus(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def get(self, job_id):
        job = self.service.get_job(job_id)
        if not job:
            return {"error": "Job not found"}, 404
        return {
            "job_id": job.job_id,
            "status": job.status,
            "study_id": job.study_id,
            "job_type": job.job_type,
            "queued_at": job.queued_at.isoformat() if job.queued_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "error_message": job.error_message,
        }


class AnalysisJobResult(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def get(self, job_id):
        job = self.service.get_job(job_id)
        if not job:
            return {"error": "Job not found"}, 404
        if job.status != "completed":
            return {"error": "Result not ready", "status": job.status}, 202
        result = json.loads(job.result_payload) if job.result_payload else {}
        return {"job_id": job.job_id, "result": result}

