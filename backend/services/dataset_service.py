from repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Business logic for dataset presentation."""

    def __init__(self, repository=None):
        self.repository = repository or DatasetRepository()

    def get_grouped_datasets(self):
        rows = self.repository.fetch_all()
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

