from sqlalchemy import text

from utils.database import get_db


class DatasetRepository:
    """Read-only access to study rows exposed as dataset catalog entries."""

    def fetch_all(self):
        db = next(get_db())
        try:
            return db.execute(
                text(
                    """
                    SELECT study_id AS id, name, type_of_cancer AS type
                    FROM studies
                    WHERE is_active = 1
                    ORDER BY type_of_cancer, name
                    """
                )
            ).mappings().all()
        finally:
            db.close()

