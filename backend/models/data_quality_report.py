from datetime import datetime

from extensions import db


class DataQualityReport(db.Model):
    __tablename__ = "data_quality_reports"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(64), nullable=False, index=True)
    study_id = db.Column(db.String(128), nullable=False, index=True)
    check_name = db.Column(db.String(128), nullable=False, index=True)
    severity = db.Column(db.String(16), nullable=False, default="info")
    status = db.Column(db.String(32), nullable=False, default="passed")
    details_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

