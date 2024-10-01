from sqlalchemy import inspect, text

from utils.database import get_db


def _use_flask_sqlalchemy_session():
    try:
        from flask import has_app_context

        return has_app_context()
    except RuntimeError:
        return False


class ClinicalRepository:
    """Read-only access for clinical records.

    Uses Flask-SQLAlchemy's session/engine inside an app context (tests + web requests)
    so ``APP_ENV=testing`` hits the same in-memory SQLite as the app. Outside app context,
    falls back to ``utils.database`` (MySQL in production / workers).
    """

    def has_table(self, table_name: str) -> bool:
        if _use_flask_sqlalchemy_session():
            from extensions import db as flask_db

            return inspect(flask_db.engine).has_table(table_name)
        db = next(get_db())
        try:
            return inspect(db.bind).has_table(table_name)
        finally:
            db.close()

    def count_patients(self, table_name):
        q = text(f"SELECT COUNT(*) AS n FROM {table_name}")
        if _use_flask_sqlalchemy_session():
            from extensions import db as flask_db

            row = flask_db.session.execute(q).mappings().first()
            return int(row["n"]) if row else 0
        db = next(get_db())
        try:
            row = db.execute(q).mappings().first()
            return int(row["n"]) if row else 0
        finally:
            db.close()

    def fetch_patients(self, table_name, limit=200, offset=0):
        query = text(
            f"SELECT patient_id, age, race, sex, ajcc_pathologic_tumor_stage, "
            f"os_status, os_months FROM {table_name} "
            f"ORDER BY patient_id LIMIT :limit OFFSET :offset"
        )
        params = {"limit": limit, "offset": offset}
        if _use_flask_sqlalchemy_session():
            from extensions import db as flask_db

            return flask_db.session.execute(query, params).mappings().all()
        db = next(get_db())
        try:
            return db.execute(query, params).mappings().all()
        finally:
            db.close()
