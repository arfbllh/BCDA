from datetime import datetime

from extensions import db


class IngestionRun(db.Model):
    __tablename__ = "ingestion_runs"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    study_id = db.Column(db.String(128), nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="queued", index=True)
    source_path = db.Column(db.Text, nullable=True)
    checksum = db.Column(db.String(128), nullable=True)
    row_counts_json = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

