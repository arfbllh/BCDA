import hashlib
import json
import os
import uuid
from datetime import datetime

from sqlalchemy import text


def _utc_now_str():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def ensure_ingestion_runs_table(engine):
    """Ensure run-tracking table exists for environments without migrations."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS ingestion_runs (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        run_id VARCHAR(64) NOT NULL UNIQUE,
        study_id VARCHAR(128) NOT NULL,
        status VARCHAR(32) NOT NULL,
        source_path TEXT NULL,
        checksum VARCHAR(128) NULL,
        row_counts_json TEXT NULL,
        error_message TEXT NULL,
        started_at DATETIME NULL,
        finished_at DATETIME NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        INDEX ix_ingestion_runs_run_id (run_id),
        INDEX ix_ingestion_runs_status (status),
        INDEX ix_ingestion_runs_study_id (study_id)
    )
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))


def compute_dataset_checksum(file_paths):
    """Build deterministic checksum from file metadata."""
    hasher = hashlib.sha256()
    for path in sorted(file_paths):
        try:
            stat = os.stat(path)
            payload = f"{path}|{stat.st_size}|{int(stat.st_mtime)}"
        except FileNotFoundError:
            payload = f"{path}|missing"
        hasher.update(payload.encode("utf-8"))
    return hasher.hexdigest()


def _fetch_existing_run(conn, study_id, checksum):
    return conn.execute(
        text(
            """
            SELECT run_id, status
            FROM ingestion_runs
            WHERE study_id = :study_id AND checksum = :checksum
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"study_id": study_id, "checksum": checksum},
    ).mappings().first()


def start_or_resume_run(engine, study_id, source_path, checksum):
    """Start a new run, skip completed one, or resume interrupted run."""
    with engine.begin() as conn:
        existing = _fetch_existing_run(conn, study_id, checksum)
        now = _utc_now_str()

        if existing and existing["status"] == "completed":
            return existing["run_id"], "skipped_completed"

        if existing and existing["status"] in {"queued", "running", "failed"}:
            conn.execute(
                text(
                    """
                    UPDATE ingestion_runs
                    SET status = 'running',
                        source_path = :source_path,
                        error_message = NULL,
                        started_at = COALESCE(started_at, :started_at),
                        finished_at = NULL,
                        updated_at = :updated_at
                    WHERE run_id = :run_id
                    """
                ),
                {
                    "run_id": existing["run_id"],
                    "source_path": source_path,
                    "started_at": now,
                    "updated_at": now,
                },
            )
            return existing["run_id"], "resumed"

        run_id = f"run_{uuid.uuid4().hex[:16]}"
        conn.execute(
            text(
                """
                INSERT INTO ingestion_runs
                (run_id, study_id, status, source_path, checksum, created_at, updated_at, started_at)
                VALUES (:run_id, :study_id, 'running', :source_path, :checksum, :created_at, :updated_at, :started_at)
                """
            ),
            {
                "run_id": run_id,
                "study_id": study_id,
                "source_path": source_path,
                "checksum": checksum,
                "created_at": now,
                "updated_at": now,
                "started_at": now,
            },
        )
        return run_id, "started"


def mark_run_completed(engine, run_id, row_counts):
    with engine.begin() as conn:
        now = _utc_now_str()
        conn.execute(
            text(
                """
                UPDATE ingestion_runs
                SET status = 'completed',
                    row_counts_json = :row_counts_json,
                    error_message = NULL,
                    finished_at = :finished_at,
                    updated_at = :updated_at
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "row_counts_json": json.dumps(row_counts),
                "finished_at": now,
                "updated_at": now,
            },
        )


def mark_run_failed(engine, run_id, error_message, row_counts=None):
    with engine.begin() as conn:
        now = _utc_now_str()
        conn.execute(
            text(
                """
                UPDATE ingestion_runs
                SET status = 'failed',
                    row_counts_json = :row_counts_json,
                    error_message = :error_message,
                    finished_at = :finished_at,
                    updated_at = :updated_at
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "row_counts_json": json.dumps(row_counts or {}),
                "error_message": (error_message or "")[:4000],
                "finished_at": now,
                "updated_at": now,
            },
        )

