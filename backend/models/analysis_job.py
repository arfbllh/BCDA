from core.datetime_util import utc_now
from extensions import db


class AnalysisJob(db.Model):
    __tablename__ = "analysis_jobs"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    study_id = db.Column(db.String(128), nullable=False, index=True)
    job_type = db.Column(db.String(64), nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="queued", index=True)
    request_payload = db.Column(db.Text, nullable=True)
    result_payload = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    queued_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

