from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class AnalysisJobCreateRequest(BaseModel):
    study_id: str = Field(min_length=1, max_length=128)
    job_type: str = Field(default="generic", min_length=1, max_length=64)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AnalysisJobCreateResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    study_id: str
    job_type: str


class AnalysisJobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    study_id: str
    job_type: str
    queued_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_message: Optional[str] = None


class AnalysisJobResultResponse(BaseModel):
    job_id: str
    result: Dict[str, Any]

