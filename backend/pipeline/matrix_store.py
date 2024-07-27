import os
from pathlib import Path

import pandas as pd

MATRIX_KEYWORDS = (
    "mrna",
    "methylation",
    "cna",
    "rppa",
    "gistic",
    "mutsig",
)


def is_matrix_file(file_path):
    name = os.path.basename(file_path).lower()
    return any(keyword in name for keyword in MATRIX_KEYWORDS)


def build_matrix_artifact_path(base_dir, dataset_name, file_path):
    source_name = Path(file_path).stem.lower()
    artifact_dir = Path(base_dir) / dataset_name / source_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir / "part-00000.parquet"


def write_matrix_parquet(df, base_dir, dataset_name, file_path, logger):
    if df is None or df.empty:
        logger.warning("Skipping empty matrix payload for %s", file_path)
        return None, 0

    artifact_path = build_matrix_artifact_path(base_dir, dataset_name, file_path)
    df.to_parquet(artifact_path, index=False)
    logger.info("Stored matrix parquet: %s (%s rows)", artifact_path, len(df.index))
    return str(artifact_path), int(len(df.index))

