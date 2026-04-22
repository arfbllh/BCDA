from core.study_tables import clinical_patient_table_name
from repositories.clinical_repository import ClinicalRepository
from repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Business logic for dataset presentation."""

    def __init__(self, repository=None, clinical_repository=None):
        self.repository = repository or DatasetRepository()
        self._clinical = clinical_repository or ClinicalRepository()

    def get_grouped_datasets(self, full_catalog: bool = False):
        rows = self.repository.fetch_all()
        if not full_catalog:
            rows = [
                row
                for row in rows
                if self._clinical.has_table(clinical_patient_table_name(row["id"]))
            ]
        grouped_datasets = {}

        for row in rows:
            dataset = {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
            }
            cancer_type = dataset["type"]
            grouped_datasets.setdefault(cancer_type, []).append(dataset)

        return grouped_datasets

