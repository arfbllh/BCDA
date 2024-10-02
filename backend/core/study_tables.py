"""Study id validation and derived SQL table names (aligned with pipeline naming)."""

import re
from pathlib import Path

from pipeline.transform import sanitize_column_name

# cBioPortal-style filename under each study directory (also used for on-demand reads).
MRNA_MATRIX_FILENAME = "data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv"

# Safe for SQL identifier fragments (matches summary / clinical routes).
STUDY_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")


def parse_study_id(dataset_name: str | None) -> str | None:
    s = (dataset_name or "").strip()
    if not s or not STUDY_ID_RE.match(s):
        return None
    return s


def clinical_patient_table_name(study_id: str) -> str:
    """Table produced by ingestion for data_clinical_patient.* under a study folder."""
    return sanitize_column_name(f"{study_id}_data_clinical_patient")


def clinical_sample_table_name(study_id: str) -> str:
    """Table produced by ingestion for data_clinical_sample.* under a study folder."""
    return sanitize_column_name(f"{study_id}_data_clinical_sample")


def mutations_table_variants(study_id: str) -> tuple[str, str]:
    """Possible MySQL table names for mutation MAF-style data (cBioPortal naming)."""
    return (
        sanitize_column_name(f"{study_id}_data_mutations"),
        sanitize_column_name(f"{study_id}_data_mutations_extended"),
    )


def gistic_genes_table_variants(study_id: str) -> tuple[str, str]:
    """GISTIC amp/del gene-level tables."""
    return (
        sanitize_column_name(f"{study_id}_data_gistic_genes_amp"),
        sanitize_column_name(f"{study_id}_data_gistic_genes_del"),
    )


def study_datasets_root() -> Path:
    from utils.config import Config

    return Path(Config.DATASETS_BASE_DIR)


def expression_matrix_path(study_id: str) -> Path:
    return study_datasets_root() / study_id / MRNA_MATRIX_FILENAME


def cbioportal_csv_triplet_paths(study_id: str) -> dict[str, Path]:
    """Standard cBioPortal-style filenames under ``DATASETS_BASE_DIR/<study_id>/``."""
    base = study_datasets_root() / study_id
    return {
        "patient": base / "data_clinical_patient.csv",
        "sample": base / "data_clinical_sample.csv",
        "meth": base / "data_methylation_hm450.csv",
    }
