from sqlalchemy import text
from utils.database import get_db


class DatasetRepository:
    """Read-only access to dataset metadata."""

    def fetch_all(self):
        db = next(get_db())
        try:
            return db.execute(text("SELECT * FROM dataset")).mappings().all()
        finally:
            db.close()

