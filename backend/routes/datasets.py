from flask_restful import Resource
from services.cache_service import cache_service
from services.dataset_service import DatasetService


class Datasets(Resource):
    def __init__(self):
        self.service = DatasetService()

    def get(self):
        """Return all datasets grouped by type"""
        try:
            cache_key = "all"
            cached = cache_service.get_json("datasets", cache_key)
            if cached is not None:
                return cached

            payload = self.service.get_grouped_datasets()
            cache_service.set_json("datasets", cache_key, payload)
            return payload
        except Exception as e:
            return {"error": str(e)}, 500