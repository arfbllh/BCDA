import os

from pipeline.discover import discover_dataset_files, discover_dataset_names, resolve_dataset_paths
from pipeline.data_quality import (
    persist_quality_reports,
    run_dataset_consistency_checks,
    run_file_quality_checks,
)
from pipeline.load import get_engine_from_config, load_single_table
from pipeline.logging_utils import get_pipeline_logger
from pipeline.matrix_store import is_matrix_file, write_matrix_parquet
from pipeline.run_tracking import (
    compute_dataset_checksum,
    ensure_data_quality_reports_table,
    ensure_ingestion_runs_table,
    mark_run_completed,
    mark_run_failed,
    start_or_resume_run,
)
from pipeline.transform import build_table_name, parse_case_list, read_dataframe
from pipeline.validate import validate_dataset_path, validate_file_path
from pipeline.verify import verify_loaded_tables

from events.ingestion_producer import flush_producer, publish_ingestion_event
from services.cache_service import cache_service
from utils.config import Config


def run_ingestion(dataset_index_path=None, datasets_base_dir=None):
    """Load cBioPortal-style bundles into MySQL / Parquet. Defaults from ``Config.DATASETS_BASE_DIR``."""
    if datasets_base_dir is None:
        datasets_base_dir = Config.DATASETS_BASE_DIR
    if dataset_index_path is None:
        dataset_index_path = os.path.join(datasets_base_dir, "datasets.csv")
    logger = get_pipeline_logger()
    engine = get_engine_from_config(Config, logger)
    ensure_ingestion_runs_table(engine)
    ensure_data_quality_reports_table(engine)

    dataset_names = discover_dataset_names(dataset_index_path)
    logger.info("Found %s datasets to process", len(dataset_names))

    for dataset_name, dataset_path in resolve_dataset_paths(datasets_base_dir, dataset_names):
        if not validate_dataset_path(dataset_path):
            logger.warning("Dataset directory not found: %s", dataset_path)
            continue

        logger.info("Loading dataset: %s", dataset_name)
        loaded_tables = []
        matrix_artifacts = {}
        quality_checks = []
        files = discover_dataset_files(dataset_path)
        logger.info("Discovered %s files for dataset %s", len(files), dataset_name)
        checksum = compute_dataset_checksum(files)
        run_id, run_state = start_or_resume_run(
            engine, dataset_name, dataset_path, checksum
        )
        logger.info(
            "Ingestion run state for %s: %s (run_id=%s)",
            dataset_name,
            run_state,
            run_id,
        )
        if run_state == "skipped_completed":
            logger.info("Skipping %s because checksum already completed", dataset_name)
            publish_ingestion_event(
                "ingestion.run.skipped",
                dataset_name,
                run_id=run_id,
                extra={"reason": "checksum_already_completed"},
            )
            continue

        publish_ingestion_event(
            "ingestion.run.started",
            dataset_name,
            run_id=run_id,
            extra={"run_state": run_state},
        )

        try:
            for file_path in files:
                if not validate_file_path(file_path):
                    logger.warning("Skipping unsupported file: %s", file_path)
                    continue

                try:
                    if "case_lists" in file_path:
                        meta_table, meta_df, cases_table, cases_df = parse_case_list(
                            file_path, dataset_name
                        )
                        quality_checks.extend(run_file_quality_checks(file_path, meta_df))
                        if not cases_df.empty:
                            quality_checks.extend(run_file_quality_checks(file_path, cases_df))
                        if load_single_table(engine, meta_table, meta_df, logger):
                            loaded_tables.append(meta_table)
                        if not cases_df.empty and load_single_table(
                            engine, cases_table, cases_df, logger
                        ):
                            loaded_tables.append(cases_table)
                        continue

                    table_name = build_table_name(dataset_name, file_path)
                    df = read_dataframe(file_path)
                    quality_checks.extend(run_file_quality_checks(file_path, df))
                    if is_matrix_file(file_path):
                        artifact_path, row_count = write_matrix_parquet(
                            df,
                            Config.MATRIX_STORAGE_DIR,
                            dataset_name,
                            file_path,
                            logger,
                        )
                        if artifact_path:
                            matrix_artifacts[artifact_path] = row_count
                        continue
                    if load_single_table(engine, table_name, df, logger):
                        loaded_tables.append(table_name)
                except Exception as exc:
                    logger.error("Failed processing %s: %s", file_path, exc)

            verification = verify_loaded_tables(engine, loaded_tables, logger)
            verification.update(matrix_artifacts)
            quality_checks.extend(run_dataset_consistency_checks(engine, dataset_name))
            persist_quality_reports(engine, run_id, dataset_name, quality_checks)
            mark_run_completed(engine, run_id, verification)
            cache_service.bump_namespace("datasets")
            cache_service.bump_namespace("clinical")
            cache_service.bump_namespace("summary")
            logger.info("Verification summary for %s: %s", dataset_name, verification)
            publish_ingestion_event(
                "ingestion.run.completed",
                dataset_name,
                run_id=run_id,
                extra={
                    "verification": dict(list(verification.items())[:200]),
                },
            )
        except Exception as exc:
            verification = verify_loaded_tables(engine, loaded_tables, logger)
            persist_quality_reports(engine, run_id, dataset_name, quality_checks)
            mark_run_failed(engine, run_id, str(exc), verification)
            logger.error("Dataset %s failed for run_id=%s: %s", dataset_name, run_id, exc)
            publish_ingestion_event(
                "ingestion.run.failed",
                dataset_name,
                run_id=run_id,
                extra={"error": str(exc)[:4000]},
            )

    flush_producer()
    logger.info("Data ingestion completed.")

