import csv
import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

from werkzeug.utils import secure_filename

from core.datetime_util import utc_now
from extensions import db
from models.upload_submission import UploadSubmission
from pipeline.orchestrator import run_ingestion
from utils.config import Config


class UploadError(Exception):
    pass


def _datasets_root() -> Path:
    return Path(Config.DATASETS_BASE_DIR)


class UploadService:
    def create_upload(self, *, file_storage, study_id: str, user_id: int) -> UploadSubmission:
        if file_storage is None:
            raise UploadError("No file uploaded.")
        filename = secure_filename(file_storage.filename or "")
        if not filename.lower().endswith(".zip"):
            raise UploadError("Only .zip study bundles are supported.")
        upload_id = f"upl_{uuid.uuid4().hex[:16]}"
        staging_dir = _datasets_root() / "_uploads" / upload_id
        staging_dir.mkdir(parents=True, exist_ok=True)
        zip_path = staging_dir / filename
        file_storage.save(str(zip_path))

        study_dir = _datasets_root() / study_id
        if study_dir.exists():
            shutil.rmtree(study_dir)
        study_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(study_dir)

        row = UploadSubmission(
            upload_id=upload_id,
            study_id=study_id,
            file_name=filename,
            file_path=str(zip_path),
            status="uploaded",
            created_by_user_id=user_id,
        )
        db.session.add(row)
        db.session.commit()
        return row

    def get_upload(self, upload_id: str) -> UploadSubmission | None:
        return UploadSubmission.query.filter_by(upload_id=upload_id).first()

    def run_ingestion_for_upload(self, row: UploadSubmission) -> UploadSubmission:
        row.status = "ingesting"
        row.updated_at = utc_now()
        db.session.commit()
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=["name"])
                writer.writeheader()
                writer.writerow({"name": row.study_id})
                index_path = fp.name
            run_ingestion(dataset_index_path=index_path, datasets_base_dir=Config.DATASETS_BASE_DIR)
            row.status = "completed"
            db.session.commit()
        except Exception as exc:
            row.status = "failed"
            row.error_message = str(exc)
            db.session.commit()
            raise
        finally:
            if "index_path" in locals() and os.path.isfile(index_path):
                os.remove(index_path)
        return row
