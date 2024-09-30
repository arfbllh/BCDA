from flask_restful import Resource

from api.error_response import api_error, internal_error_response
from core.study_tables import parse_study_id
from core.pagination import clinical_list_params
from services.cache_service import cache_service
from services.clinical_service import ClinicalService


class ClinicalData(Resource):
    def __init__(self):
        self.service = ClinicalService()

    def get(self, dataset_name):
        """Return clinical rows for a dataset (optional ?limit=&offset=, capped)."""
        try:
            if parse_study_id(dataset_name) is None:
                return api_error("INVALID_REQUEST", "Invalid study id."), 400
            if not self.service.clinical_ready(dataset_name):
                return (
                    api_error(
                        "NOT_INGESTED",
                        "No clinical data table for this study. Add cBioPortal-style files "
                        "under DATASETS_BASE_DIR and run the ingestion pipeline.",
                    ),
                    404,
                )
            limit, offset = clinical_list_params()
            cache_key = f"{dataset_name}:{limit}:{offset}"
            cached = cache_service.get_json("clinical", cache_key)
            if cached is not None:
                return cached, 200

            total = self.service.count_clinical_patients(dataset_name)
            rows = self.service.get_clinical_data(dataset_name, limit=limit, offset=offset)
            payload = {
                "items": rows,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
            cache_service.set_json("clinical", cache_key, payload)
            return payload, 200
        except Exception:
            return internal_error_response(
                f"GET /clinical/{dataset_name} failed",
            ), 500
