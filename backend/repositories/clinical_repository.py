from sqlalchemy import inspect, text

from utils.database import get_db


class ClinicalRepository:
    """Read-only access for clinical records."""

    def has_table(self, table_name: str) -> bool:
        db = next(get_db())
        try:
            return inspect(db.bind).has_table(table_name)
        finally:
            db.close()

    def count_patients(self, table_name):
        db = next(get_db())
        try:
            q = text(f"SELECT COUNT(*) AS n FROM {table_name}")
            row = db.execute(q).mappings().first()
            return int(row["n"]) if row else 0
        finally:
            db.close()

    def fetch_patients(self, table_name, limit=200, offset=0):
        db = next(get_db())
        try:
            query = text(
                f"SELECT patient_id, age, race, sex, ajcc_pathologic_tumor_stage, "
                f"os_status, os_months FROM {table_name} "
                f"ORDER BY patient_id LIMIT :limit OFFSET :offset"
            )
            return db.execute(query, {"limit": limit, "offset": offset}).mappings().all()
        finally:
            db.close()

