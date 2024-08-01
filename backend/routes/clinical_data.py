from flask_restful import Resource
from services.cache_service import cache_service
from services.clinical_service import ClinicalService


class ClinicalData(Resource):
    def __init__(self):
        self.service = ClinicalService()

    def get(self, dataset_name):
        """Return clinical data for a specific dataset"""
        try:
            cache_key = f"{dataset_name}:default"
            cached = cache_service.get_json("clinical", cache_key)
            if cached is not None:
                return cached, 200

            payload = self.service.get_clinical_data(dataset_name)
            cache_service.set_json("clinical", cache_key, payload)
            return payload, 200
        except Exception as e:
            return {"error": str(e)}, 500
