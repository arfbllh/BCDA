"""Flask app factory and top-level wiring."""

import os

from flask import Flask, jsonify
from flask_cors import CORS

from api.openapi import OPENAPI_SPEC
from api.v1 import register_legacy_routes, register_v1_routes
from core.config import get_config
from extensions import db, migrate
from workers.celery_app import init_celery


def _parse_origins(origins_value):
    if not origins_value:
        return "*"
    if "," in origins_value:
        return [origin.strip() for origin in origins_value.split(",") if origin.strip()]
    return origins_value.strip()


def create_app():
    """Create and configure Flask app instance."""
    app = Flask(__name__)
    config_class = get_config(os.getenv("APP_ENV"))
    app.config.from_object(config_class)

    cors_origins = _parse_origins(app.config.get("CORS_ORIGINS", "*"))
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    db.init_app(app)
    migrate.init_app(app, db)
    init_celery(app)

    # Ensure model metadata is registered for migration autogeneration.
    import models  # noqa: F401
    import workers.tasks  # noqa: F401

    register_v1_routes(app)
    register_legacy_routes(app)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "env": os.getenv("APP_ENV", "development")})

    @app.get("/readyz")
    def readyz():
        return jsonify({"ready": True})

    @app.get("/api/v1/openapi.json")
    def openapi_spec_v1():
        return jsonify(OPENAPI_SPEC)

    @app.get("/api/openapi.json")
    def openapi_spec_legacy():
        return jsonify(OPENAPI_SPEC)

    return app

