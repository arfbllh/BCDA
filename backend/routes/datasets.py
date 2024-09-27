from flask_restful import Resource

from api.error_response import internal_error_response
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
        except Exception:
            return internal_error_response("GET /datasets failed"), 500