from core.study_tables import clinical_patient_table_name, parse_study_id
from repositories.clinical_repository import ClinicalRepository


class ClinicalService:
    """Business logic for clinical payloads."""

    def __init__(self, repository=None):
        self.repository = repository or ClinicalRepository()

    def get_clinical_data(self, dataset_name, limit=200, offset=0):
        study = parse_study_id(dataset_name)
        if study is None:
            return []
        table_name = clinical_patient_table_name(study)
        if not self.repository.has_table(table_name):
            return []
        rows = self.repository.fetch_patients(
            table_name=table_name, limit=limit, offset=offset
        )

        clinical_data = []
        for row in rows:
            status = row["os_status"] or ""
            clinical_data.append(
                {
                    "patient_id": row["patient_id"],
                    "age": row["age"],
                    "race": row["race"],
                    "gender": row["sex"],
                    "stage": row["ajcc_pathologic_tumor_stage"],
                    "status": "Alive" if status[:1] == "0" else "DECEASED",
                    "survival_months": row["os_months"],
                }
            )

        return clinical_data

    def count_clinical_patients(self, dataset_name):
        study = parse_study_id(dataset_name)
        if study is None:
            return 0
        table_name = clinical_patient_table_name(study)
        if not self.repository.has_table(table_name):
            return 0
        return self.repository.count_patients(table_name)

    def clinical_ready(self, dataset_name: str) -> bool:
        study = parse_study_id(dataset_name)
        if study is None:
            return False
        return self.repository.has_table(clinical_patient_table_name(study))

