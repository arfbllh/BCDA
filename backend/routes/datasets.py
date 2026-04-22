from flask import request
from flask_restful import Resource

from api.error_response import internal_error_response
from services.cache_service import cache_service
from services.dataset_service import DatasetService


def _truthy_full_catalog(val: str | None) -> bool:
    if val is None:
        return False
    return val.strip().lower() in ("1", "true", "yes", "full")


class Datasets(Resource):
    def __init__(self):
        self.service = DatasetService()

    def get(self):
        """Return datasets grouped by type.

        By default only studies with an ingested clinical patient table are listed.
        Pass ``?full_catalog=1`` to include all active catalog rows (operators / deep links).
        """
        try:
            full_catalog = _truthy_full_catalog(request.args.get("full_catalog"))
            cache_key = "full" if full_catalog else "ingested"
            cached = cache_service.get_json("datasets", cache_key)
            if cached is not None:
                return cached

            payload = self.service.get_grouped_datasets(full_catalog=full_catalog)
            cache_service.set_json("datasets", cache_key, payload)
            return payload
        except Exception:
            return internal_error_response("GET /datasets failed"), 500