"""Operational: whether a study has ingested clinical tables and raw matrix files on disk."""

from flask_restful import Resource

from api.error_response import api_error
from core.study_tables import (
    clinical_patient_table_name,
    clinical_sample_table_name,
    expression_matrix_path,
    gistic_genes_table_variants,
    mutations_table_variants,
    parse_study_id,
)
from repositories.clinical_repository import ClinicalRepository


def _first_existing_table(repo: ClinicalRepository, names: tuple[str, ...]) -> str | None:
    for name in names:
        if repo.has_table(name):
            return name
    return None


class StudyDataStatus(Resource):
    """GET /datasets/<study_id>/data-status — ingestion / file presence flags."""

    def __init__(self):
        self._clinical_repo = ClinicalRepository()

    def get(self, dataset_name):
        study = parse_study_id(dataset_name)
        if study is None:
            return api_error("INVALID_REQUEST", "Invalid study id."), 400
        patient_table = clinical_patient_table_name(study)
        sample_table = clinical_sample_table_name(study)
        clinical_patient = self._clinical_repo.has_table(patient_table)
        clinical_sample = self._clinical_repo.has_table(sample_table)
        mutations_table = _first_existing_table(
            self._clinical_repo, mutations_table_variants(study)
        )
        gistic_table = _first_existing_table(
            self._clinical_repo, gistic_genes_table_variants(study)
        )
        matrix_path = expression_matrix_path(study)
        summary_ready = (
            clinical_patient
            and clinical_sample
            and mutations_table is not None
            and gistic_table is not None
        )
        return (
            {
                "study_id": study,
                "clinical_patient_ingested": clinical_patient,
                "clinical_sample_ingested": clinical_sample,
                "mutations_table": mutations_table,
                "gistic_table": gistic_table,
                "summary_ready": summary_ready,
                "expression_matrix_file_present": matrix_path.is_file(),
            },
            200,
        )
