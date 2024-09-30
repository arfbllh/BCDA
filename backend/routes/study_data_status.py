"""Operational: whether a study has ingested clinical tables and raw matrix files on disk."""

from flask_restful import Resource

from api.error_response import api_error
from core.study_tables import (
    clinical_patient_table_name,
    expression_matrix_path,
    parse_study_id,
)
from repositories.clinical_repository import ClinicalRepository


class StudyDataStatus(Resource):
    """GET /datasets/<study_id>/data-status — ingestion / file presence flags."""

    def __init__(self):
        self._clinical_repo = ClinicalRepository()

    def get(self, dataset_name):
        study = parse_study_id(dataset_name)
        if study is None:
            return api_error("INVALID_REQUEST", "Invalid study id."), 400
        clinical_table = clinical_patient_table_name(study)
        matrix_path = expression_matrix_path(study)
        return (
            {
                "study_id": study,
                "clinical_patient_ingested": self._clinical_repo.has_table(clinical_table),
                "expression_matrix_file_present": matrix_path.is_file(),
            },
            200,
        )
