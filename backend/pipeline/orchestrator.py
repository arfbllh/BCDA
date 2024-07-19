from pipeline.discover import discover_dataset_files, discover_dataset_names, resolve_dataset_paths
from pipeline.load import get_engine_from_config, load_single_table
from pipeline.logging_utils import get_pipeline_logger
from pipeline.transform import build_table_name, parse_case_list, read_dataframe
from pipeline.validate import validate_dataset_path, validate_file_path
from pipeline.verify import verify_loaded_tables
from utils.config import Config


def run_ingestion(dataset_index_path="./datasets/datasets.csv", datasets_base_dir="datasets"):
    logger = get_pipeline_logger()
    engine = get_engine_from_config(Config, logger)

    dataset_names = discover_dataset_names(dataset_index_path)
    logger.info("Found %s datasets to process", len(dataset_names))

    for dataset_name, dataset_path in resolve_dataset_paths(datasets_base_dir, dataset_names):
        if not validate_dataset_path(dataset_path):
            logger.warning("Dataset directory not found: %s", dataset_path)
            continue

        logger.info("Loading dataset: %s", dataset_name)
        loaded_tables = []
        files = discover_dataset_files(dataset_path)
        logger.info("Discovered %s files for dataset %s", len(files), dataset_name)

        for file_path in files:
            if not validate_file_path(file_path):
                logger.warning("Skipping unsupported file: %s", file_path)
                continue

            try:
                if "case_lists" in file_path:
                    meta_table, meta_df, cases_table, cases_df = parse_case_list(
                        file_path, dataset_name
                    )
                    if load_single_table(engine, meta_table, meta_df, logger):
                        loaded_tables.append(meta_table)
                    if not cases_df.empty and load_single_table(
                        engine, cases_table, cases_df, logger
                    ):
                        loaded_tables.append(cases_table)
                    continue

                table_name = build_table_name(dataset_name, file_path)
                df = read_dataframe(file_path)
                if load_single_table(engine, table_name, df, logger):
                    loaded_tables.append(table_name)
            except Exception as exc:
                logger.error("Failed processing %s: %s", file_path, exc)

        verification = verify_loaded_tables(engine, loaded_tables, logger)
        logger.info("Verification summary for %s: %s", dataset_name, verification)

    logger.info("Data ingestion completed.")

