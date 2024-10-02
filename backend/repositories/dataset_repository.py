from sqlalchemy import text

from utils.database import get_db


def _use_flask_sqlalchemy_session():
    try:
        from flask import has_app_context

        return has_app_context()
    except RuntimeError:
        return False


class DatasetRepository:
    """Read-only access to study rows exposed as dataset catalog entries.

    Uses Flask-SQLAlchemy inside an app context (tests + web) so the catalog matches
    the same engine as ORM models; otherwise ``utils.database`` (MySQL) for workers.
    """

    def fetch_all(self):
        q = text(
            """
            SELECT study_id AS id, name, type_of_cancer AS type
            FROM studies
            WHERE is_active = 1
            ORDER BY type_of_cancer, name
            """
        )
        if _use_flask_sqlalchemy_session():
            from extensions import db as flask_db

            return flask_db.session.execute(q).mappings().all()
        db = next(get_db())
        try:
            return db.execute(q).mappings().all()
        finally:
            db.close()

