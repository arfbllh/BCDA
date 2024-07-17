from flask_restful import Resource
from services.clinical_service import ClinicalService


class ClinicalData(Resource):
    def __init__(self):
        self.service = ClinicalService()

    def get(self, dataset_name):
        """Return clinical data for a specific dataset"""
        try:
            return self.service.get_clinical_data(dataset_name), 200
        except Exception as e:
            return {"error": str(e)}, 500
