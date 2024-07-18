"""API v1 routing registration."""

from flask_restful import Api
from routes.analysis import Analysis
from routes.clinical_data import ClinicalData
from routes.datasets import Datasets
from routes.heatmap import Heatmap
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
    api.add_resource(Heatmap, "/api/v1/datasets/heatmap", endpoint="v1_heatmap")


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
    api.add_resource(Heatmap, "/api/datasets/heatmap", endpoint="legacy_heatmap")

