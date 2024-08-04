import json

from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from api.error_response import api_error
from schemas.analysis_job_schemas import (
    AnalysisJobCreateRequest,
    AnalysisJobCreateResponse,
    AnalysisJobResultResponse,
    AnalysisJobStatusResponse,
)
from services.analysis_job_service import AnalysisJobService


class AnalysisJobs(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def post(self):
        try:
            payload = request.get_json(silent=True) or {}
            validated = AnalysisJobCreateRequest.model_validate(payload)
            job = self.service.create_job(
                study_id=validated.study_id,
                job_type=validated.job_type,
                payload={
                    "study_id": validated.study_id,
                    "job_type": validated.job_type,
                    "parameters": validated.parameters,
                },
            )
            response = AnalysisJobCreateResponse(
                job_id=job.job_id,
                status=job.status,
                study_id=job.study_id,
                job_type=job.job_type,
            )
            return response.model_dump(), 202
        except ValidationError as exc:
            return api_error("VALIDATION_ERROR", exc.errors()), 400


class AnalysisJobStatus(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def get(self, job_id):
        job = self.service.get_job(job_id)
        if not job:
            return api_error("JOB_NOT_FOUND", "Job not found"), 404
        response = AnalysisJobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            study_id=job.study_id,
            job_type=job.job_type,
            queued_at=job.queued_at.isoformat() if job.queued_at else None,
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
            error_message=job.error_message,
        )
        return response.model_dump()


class AnalysisJobResult(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def get(self, job_id):
        job = self.service.get_job(job_id)
        if not job:
            return api_error("JOB_NOT_FOUND", "Job not found"), 404
        if job.status != "completed":
            return api_error("RESULT_NOT_READY", f"Result not ready; status={job.status}"), 202
        result = json.loads(job.result_payload) if job.result_payload else {}
        response = AnalysisJobResultResponse(job_id=job.job_id, result=result)
        return response.model_dump()

