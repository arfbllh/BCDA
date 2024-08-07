import json

import pandas as pd
from sqlalchemy import text


def run_file_quality_checks(file_path, df):
    """Run lightweight quality checks on a loaded dataframe."""
    checks = []
    if df is None:
        checks.append(
            {
                "check_name": "dataframe_loaded",
                "severity": "error",
                "status": "failed",
                "details": {"file_path": file_path, "reason": "unreadable_or_unsupported"},
            }
        )
        return checks

    row_count = int(len(df.index))
    column_count = int(len(df.columns))
    checks.append(
        {
            "check_name": "row_count_positive",
            "severity": "error",
            "status": "passed" if row_count > 0 else "failed",
            "details": {"file_path": file_path, "row_count": row_count},
        }
    )
    checks.append(
        {
            "check_name": "column_count_positive",
            "severity": "error",
            "status": "passed" if column_count > 0 else "failed",
            "details": {"file_path": file_path, "column_count": column_count},
        }
    )

    null_ratio = float(df.isna().mean().mean()) if row_count > 0 and column_count > 0 else 1.0
    checks.append(
        {
            "check_name": "null_ratio_threshold",
            "severity": "warn",
            "status": "passed" if null_ratio <= 0.70 else "failed",
            "details": {"file_path": file_path, "null_ratio": round(null_ratio, 4)},
        }
    )
    return checks


def run_dataset_consistency_checks(engine, dataset_name):
    """Run consistency checks after ingestion completes."""
    checks = []
    patient_table = f"{dataset_name}_data_clinical_patient"
    sample_table = f"{dataset_name}_data_clinical_sample"

    with engine.connect() as conn:
        # table existence checks
        for table_name in (patient_table, sample_table):
            exists = conn.execute(
                text(
                    """
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = DATABASE() AND table_name = :table_name
                    """
                ),
                {"table_name": table_name},
            ).scalar()
            checks.append(
                {
                    "check_name": f"table_exists_{table_name}",
                    "severity": "warn",
                    "status": "passed" if exists else "failed",
                    "details": {"table_name": table_name},
                }
            )

        # patient/sample key quality when both tables exist
        patient_exists = any(
            c["check_name"] == f"table_exists_{patient_table}" and c["status"] == "passed"
            for c in checks
        )
        sample_exists = any(
            c["check_name"] == f"table_exists_{sample_table}" and c["status"] == "passed"
            for c in checks
        )
        if patient_exists and sample_exists:
            orphan_count = conn.execute(
                text(
                    f"""
                    SELECT COUNT(*) FROM {sample_table} s
                    LEFT JOIN {patient_table} p
                    ON s.patient_id = p.patient_id
                    WHERE p.patient_id IS NULL
                    """
                )
            ).scalar()
            checks.append(
                {
                    "check_name": "sample_patient_orphans",
                    "severity": "warn",
                    "status": "passed" if int(orphan_count or 0) == 0 else "failed",
                    "details": {"orphan_count": int(orphan_count or 0)},
                }
            )

    return checks


def persist_quality_reports(engine, run_id, study_id, checks):
    if not checks:
        return
    with engine.begin() as conn:
        for check in checks:
            conn.execute(
                text(
                    """
                    INSERT INTO data_quality_reports
                    (run_id, study_id, check_name, severity, status, details_json, created_at)
                    VALUES (:run_id, :study_id, :check_name, :severity, :status, :details_json, NOW())
                    """
                ),
                {
                    "run_id": run_id,
                    "study_id": study_id,
                    "check_name": check["check_name"],
                    "severity": check.get("severity", "info"),
                    "status": check.get("status", "passed"),
                    "details_json": json.dumps(check.get("details", {}), default=str),
                },
            )

