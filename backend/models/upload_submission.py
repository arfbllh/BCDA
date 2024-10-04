from core.datetime_util import utc_now
from extensions import db


class UploadSubmission(db.Model):
    __tablename__ = "upload_submissions"

    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    study_id = db.Column(db.String(128), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="uploaded", index=True)
    ingestion_run_id = db.Column(db.String(64), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)
