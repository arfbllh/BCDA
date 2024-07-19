import os
from pathlib import Path

import pandas as pd


def discover_dataset_names(dataset_index_path):
    """Read dataset names from CSV index."""
    df = pd.read_csv(dataset_index_path)
    return df["name"].dropna().astype(str).tolist()


def discover_dataset_files(dataset_path):
    """Discover supported files in a dataset directory."""
    dataset_dir = Path(dataset_path)
    files = []

    for pattern in ("*.csv", "*.txt", "*.tsv", "*.seg"):
        files.extend(dataset_dir.glob(pattern))

    case_list_dir = dataset_dir / "case_lists"
    if case_list_dir.is_dir():
        for pattern in ("*.txt", "*.csv", "*.tsv"):
            files.extend(case_list_dir.glob(pattern))

    return sorted({str(path) for path in files})


def resolve_dataset_paths(base_dir, dataset_names):
    """Build filesystem paths for dataset names."""
    for dataset_name in dataset_names:
        yield dataset_name, os.path.join(base_dir, dataset_name)

