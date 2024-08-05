import os
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    os.environ["APP_ENV"] = "testing"
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
    os.environ["TEST_DATABASE_URI"] = "sqlite:///:memory:"


@pytest.fixture()
def app():
    from core.app_factory import create_app
    from extensions import db

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
