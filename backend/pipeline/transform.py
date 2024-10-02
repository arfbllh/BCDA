import os
import re

import pandas as pd


def sanitize_column_name(col_name):
    sanitized = re.sub(r"[^\w]", "_", str(col_name))
    if sanitized and sanitized[0].isdigit():
        sanitized = "c_" + sanitized
    if len(sanitized) > 64:
        sanitized = sanitized[:64]
    return sanitized.lower()


def build_table_name(dataset_name, file_path):
    file_name = os.path.basename(file_path)
    file_type = file_name.split(".")[0]

    if "case_lists" in file_path:
        table_name = f"{dataset_name}_case_list_{file_type}"
    else:
        table_name = f"{dataset_name}_{file_type}"
    return sanitize_column_name(table_name)


def parse_case_list(file_path, dataset_name):
    metadata = {}
    case_ids = []
    with open(file_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("case_list_ids:"):
                case_ids_str = line.split(":", 1)[1].strip()
                case_ids = [cid for cid in re.split(r"\s+", case_ids_str) if cid]
            elif ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

    stable_id = metadata.get("stable_id", "case_list")
    meta_table_name = sanitize_column_name(f"{dataset_name}_meta_{stable_id}")
    cases_table_name = sanitize_column_name(f"{dataset_name}_cases_{stable_id}")

    meta_df = pd.DataFrame([metadata]) if metadata else pd.DataFrame([{}])
    cases_df = pd.DataFrame(
        [{"case_id": case_id, "stable_id": stable_id, "dataset": dataset_name} for case_id in case_ids]
    )
    return meta_table_name, meta_df, cases_table_name, cases_df


def read_dataframe(file_path):
    lower = file_path.lower()
    if lower.endswith((".txt", ".tsv")):
        try:
            return pd.read_csv(file_path, sep="\t", comment="#")
        except Exception:
            return pd.read_csv(file_path, sep="\t", comment="#", header=None)
    if lower.endswith(".csv"):
        return pd.read_csv(file_path)
    if lower.endswith(".seg"):
        return pd.read_csv(file_path)
    return None

