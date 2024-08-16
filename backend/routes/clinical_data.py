from flask_restful import Resource

from core.pagination import clinical_list_params
from services.cache_service import cache_service
from services.clinical_service import ClinicalService


class ClinicalData(Resource):
    def __init__(self):
        self.service = ClinicalService()

    def get(self, dataset_name):
        """Return clinical rows for a dataset (optional ?limit=&offset=, capped)."""
        try:
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
        except Exception as e:
            return {"error": str(e)}, 500
