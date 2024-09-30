"""API v1 routing registration."""

from flask_restful import Api
from routes.analysis import Analysis
from routes.analysis_jobs import AnalysisJobResult, AnalysisJobs, AnalysisJobStatus
from routes.clinical_data import ClinicalData
from routes.datasets import Datasets
from routes.heatmap import Heatmap
from routes.study_data_status import StudyDataStatus
from routes.summary import Summary


def register_v1_routes(app):
    """Register versioned API routes."""
    api = Api(app)
    api.add_resource(Datasets, "/api/v1/datasets", endpoint="v1_datasets")
    api.add_resource(
        ClinicalData,
        "/api/v1/datasets/<dataset_name>/clinical",
        endpoint="v1_clinical_data",
    )
    api.add_resource(
        Summary,
        "/api/v1/datasets/<dataset_name>/summary",
        endpoint="v1_summary",
    )
    api.add_resource(
        Analysis,
        "/api/v1/datasets/<dataset_name>/analysis",
        endpoint="v1_analysis",
    )
    api.add_resource(
        StudyDataStatus,
        "/api/v1/datasets/<dataset_name>/data-status",
        endpoint="v1_study_data_status",
    )
    api.add_resource(
        Heatmap,
        "/api/v1/datasets/<dataset_name>/heatmap",
        endpoint="v1_heatmap",
    )
    api.add_resource(AnalysisJobs, "/api/v1/analysis/jobs", endpoint="v1_analysis_jobs")
    api.add_resource(
        AnalysisJobStatus,
        "/api/v1/analysis/jobs/<job_id>",
        endpoint="v1_analysis_job_status",
    )
    api.add_resource(
        AnalysisJobResult,
        "/api/v1/analysis/jobs/<job_id>/result",
        endpoint="v1_analysis_job_result",
    )


def register_legacy_routes(app):
    """Temporary compatibility layer for existing frontend routes."""
    api = Api(app)
    api.add_resource(Datasets, "/api/datasets", endpoint="legacy_datasets")
    api.add_resource(
        ClinicalData,
        "/api/datasets/<dataset_name>/clinical",
        endpoint="legacy_clinical_data",
    )
    api.add_resource(
        Summary,
        "/api/datasets/<dataset_name>/summary",
        endpoint="legacy_summary",
    )
    api.add_resource(
        Analysis,
        "/api/datasets/<dataset_name>/analysis",
        endpoint="legacy_analysis",
    )
    api.add_resource(
        StudyDataStatus,
        "/api/datasets/<dataset_name>/data-status",
        endpoint="legacy_study_data_status",
    )
    api.add_resource(
        Heatmap,
        "/api/datasets/<dataset_name>/heatmap",
        endpoint="legacy_heatmap",
    )
    api.add_resource(AnalysisJobs, "/api/analysis/jobs", endpoint="legacy_analysis_jobs")
    api.add_resource(
        AnalysisJobStatus,
        "/api/analysis/jobs/<job_id>",
        endpoint="legacy_analysis_job_status",
    )
    api.add_resource(
        AnalysisJobResult,
        "/api/analysis/jobs/<job_id>/result",
        endpoint="legacy_analysis_job_result",
    )

