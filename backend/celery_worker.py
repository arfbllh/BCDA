"""Celery worker entry: bootstrap Flask app so broker config and tasks load correctly."""

from core.app_factory import create_app

create_app()

from workers.celery_app import celery_app  # noqa: E402

__all__ = ["celery_app"]
