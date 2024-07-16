"""Flask app factory and top-level wiring."""

from flask import Flask, jsonify
from flask_cors import CORS

from api.v1 import register_legacy_routes, register_v1_routes


def create_app():
    """Create and configure Flask app instance."""
    app = Flask(__name__)
    CORS(app)

    register_v1_routes(app)
    register_legacy_routes(app)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    return app

