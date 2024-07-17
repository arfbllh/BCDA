"""Flask app factory and top-level wiring."""

import os

from flask import Flask, jsonify
from flask_cors import CORS

from api.v1 import register_legacy_routes, register_v1_routes
from core.config import get_config


def create_app():
    """Create and configure Flask app instance."""
    app = Flask(__name__)
    config_class = get_config(os.getenv("APP_ENV"))
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    register_v1_routes(app)
    register_legacy_routes(app)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "env": os.getenv("APP_ENV", "development")})

    return app

