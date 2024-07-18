from datetime import datetime

from extensions import db


class Study(db.Model):
    __tablename__ = "studies"

    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    type_of_cancer = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    citation = db.Column(db.String(255), nullable=True)
    pmid = db.Column(db.String(32), nullable=True)
    source = db.Column(db.String(128), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

