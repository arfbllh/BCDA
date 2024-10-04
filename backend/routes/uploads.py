from flask import g, request
from flask_restful import Resource

from api.error_response import api_error
from routes.auth_guard import require_auth
from services.upload_service import UploadError, UploadService
from workers.tasks import process_upload_ingestion


class DatasetUpload(Resource):
    def __init__(self):
        self.service = UploadService()

    @require_auth
    def post(self):
        study_id = (request.form.get("study_id") or "").strip()
        if not study_id:
            return api_error("VALIDATION_ERROR", "study_id is required."), 400
        file_storage = request.files.get("file")
        try:
            row = self.service.create_upload(
                file_storage=file_storage,
                study_id=study_id,
                user_id=g.current_user.id,
            )
        except UploadError as exc:
            return api_error("UPLOAD_ERROR", str(exc)), 400
        return {
            "upload_id": row.upload_id,
            "study_id": row.study_id,
            "status": row.status,
        }, 201


class DatasetUploadIngest(Resource):
    def __init__(self):
        self.service = UploadService()

    @require_auth
    def post(self, upload_id):
        row = self.service.get_upload(upload_id)
        if row is None:
            return api_error("NOT_FOUND", "Upload not found."), 404
        process_upload_ingestion.delay(upload_id)
        return {"upload_id": row.upload_id, "status": "queued"}, 202


class DatasetUploadStatus(Resource):
    def __init__(self):
        self.service = UploadService()

    @require_auth
    def get(self, upload_id):
        row = self.service.get_upload(upload_id)
        if row is None:
            return api_error("NOT_FOUND", "Upload not found."), 404
        return {
            "upload_id": row.upload_id,
            "study_id": row.study_id,
            "status": row.status,
            "ingestion_run_id": row.ingestion_run_id,
            "error_message": row.error_message,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }, 200
