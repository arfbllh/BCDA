from sqlalchemy import text
from utils.database import get_db


class ClinicalRepository:
    """Read-only access for clinical records."""

    def fetch_patients(self, table_name, limit=200):
        db = next(get_db())
        try:
            query = text(
                f"SELECT patient_id, age, race, sex, ajcc_pathologic_tumor_stage, "
                f"os_status, os_months FROM {table_name} LIMIT {limit}"
            )
            return db.execute(query).mappings().all()
        finally:
            db.close()

