from flask_restful import Resource
from services.dataset_service import DatasetService


class Datasets(Resource):
    def __init__(self):
        self.service = DatasetService()

    def get(self):
        """Return all datasets grouped by type"""
        try:
            return self.service.get_grouped_datasets()
        except Exception as e:
            return {"error": str(e)}, 500