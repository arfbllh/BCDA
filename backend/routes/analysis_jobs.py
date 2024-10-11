"""REST resources for async analysis jobs (survival, llm_infer, etc.)."""

import json

from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from api.error_response import api_error, format_pydantic_errors
from schemas.analysis_job_schemas import (
    AnalysisJobCreateRequest,
    AnalysisJobCreateResponse,
    AnalysisJobResultResponse,
    AnalysisJobStatusResponse,
)
from services.analysis_job_service import AnalysisJobService


def _job_or_not_found(service: AnalysisJobService, job_id: str):
    """Return (job, None) or (None, (body, status_code))."""
    job = service.get_job(job_id)
    if job is None:
        return None, (api_error("JOB_NOT_FOUND", "Job not found"), 404)
    return job, None


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
            return api_error("VALIDATION_ERROR", format_pydantic_errors(exc.errors())), 400
        except Exception:
            return api_error(
                "INTERNAL_ERROR",
                "Failed to create analysis job. Ensure worker/broker is available or retry.",
            ), 500


class AnalysisJobStatus(Resource):
    def __init__(self):
        self.service = AnalysisJobService()

    def get(self, job_id):
        job, err = _job_or_not_found(self.service, job_id)
        if err:
            return err
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
        job, err = _job_or_not_found(self.service, job_id)
        if err:
            return err
        if job.status != "completed":
            return api_error("RESULT_NOT_READY", f"Result not ready; status={job.status}"), 202
        result = json.loads(job.result_payload) if job.result_payload else {}
        response = AnalysisJobResultResponse(job_id=job.job_id, result=result)
        return response.model_dump()

