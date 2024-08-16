from repositories.clinical_repository import ClinicalRepository


class ClinicalService:
    """Business logic for clinical payloads."""

    def __init__(self, repository=None):
        self.repository = repository or ClinicalRepository()

    def get_clinical_data(self, dataset_name, limit=200, offset=0):
        # Preserve current behavior until schema normalization PRs.
        table_name = "brca_tcga_pub2015_data_clinical_patient"
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
        table_name = "brca_tcga_pub2015_data_clinical_patient"
        return self.repository.count_patients(table_name)

