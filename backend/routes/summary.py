"""Summary statistics for a study (cBioPortal-style `{study}_data_*` table names)."""

import re
from http import HTTPStatus

import numpy as np
import pandas as pd
from flask_restful import Resource
from lifelines import KaplanMeierFitter
from sqlalchemy import text

from api.error_response import api_error, internal_error_response
from core.study_tables import parse_study_id
from repositories.clinical_repository import ClinicalRepository
from services.cache_service import cache_service
from utils.database import get_db


def _study_tables(dataset_name: str):
    study = parse_study_id(dataset_name)
    if study is None:
        return None
    return {
        "study": study,
        "patient": f"{study}_data_clinical_patient",
        "sample": f"{study}_data_clinical_sample",
    }


def _first_existing_table(repo: ClinicalRepository, candidates: tuple[str, ...]) -> str | None:
    for name in candidates:
        if repo.has_table(name):
            return name
    return None


class Summary(Resource):
    def get(self, dataset_name):
        try:
            tables = _study_tables(dataset_name)
            if tables is None:
                return api_error("INVALID_REQUEST", "Invalid study id."), HTTPStatus.BAD_REQUEST

            study = tables["study"]
            patient_table = tables["patient"]
            sample_table = tables["sample"]

            cache_key = f"{study}:full"
            cached = cache_service.get_json("summary", cache_key)
            if cached is not None:
                return cached, HTTPStatus.OK

            repo = ClinicalRepository()
            mutations_table = _first_existing_table(
                repo,
                (f"{study}_data_mutations", f"{study}_data_mutations_extended"),
            )
            gistic_table = _first_existing_table(
                repo,
                (f"{study}_data_gistic_genes_amp", f"{study}_data_gistic_genes_del"),
            )
            missing = [t for t in (patient_table, sample_table) if not repo.has_table(t)]
            if mutations_table is None:
                missing.append(
                    f"{study}_data_mutations or {study}_data_mutations_extended"
                )
            if gistic_table is None:
                missing.append(
                    f"{study}_data_gistic_genes_amp or {study}_data_gistic_genes_del"
                )
            if missing:
                return (
                    api_error(
                        "NOT_INGESTED",
                        "Summary needs ingested cBioPortal-style tables for this study "
                        f"(missing: {', '.join(missing)}). From backend/, run ingestion after "
                        "placing study files under DATASETS_BASE_DIR.",
                    ),
                    HTTPStatus.NOT_FOUND,
                )

            response_data = {}
            db = next(get_db())

            # ===== PIE CHARTS =====

            samples_count = db.execute(
                text(f"SELECT COUNT(DISTINCT id) FROM {sample_table}")
            ).scalar()
            patients_count = db.execute(
                text(f"SELECT COUNT(DISTINCT patient_id) FROM {patient_table}")
            ).scalar()

            response_data["samplesPerPatient"] = [
                {"category": "Samples", "value": samples_count},
                {"category": "Patients", "value": patients_count},
            ]

            living_count = db.execute(
                text(
                    f"SELECT COUNT(DISTINCT patient_id) FROM {patient_table} "
                    f"WHERE os_status = '0:LIVING'"
                )
            ).scalar()
            deceased_count = db.execute(
                text(
                    f"SELECT COUNT(DISTINCT patient_id) FROM {patient_table} "
                    f"WHERE os_status = '1:DECEASED'"
                )
            ).scalar()

            response_data["overallSurvivalStatus"] = [
                {"category": "Living", "value": living_count},
                {"category": "Deceased", "value": deceased_count},
            ]

            primary_count = db.execute(
                text(
                    f"SELECT count(*) FROM {sample_table} WHERE sample_type = 'primary'"
                )
            ).scalar()
            metastasis_count = db.execute(
                text(
                    f"SELECT count(*) FROM {sample_table} WHERE sample_type <> 'primary'"
                )
            ).scalar()

            response_data["sampleType"] = [
                {"category": "Primary", "value": primary_count},
                {"category": "Metastasis", "value": metastasis_count},
            ]

            male = db.execute(
                text(f"SELECT count(*) FROM {patient_table} where sex = 'male'")
            ).scalar()
            female = db.execute(
                text(f"SELECT count(*) FROM {patient_table} where sex = 'female'")
            ).scalar()
            response_data["sex"] = [
                {"category": "Female", "value": female},
                {"category": "Male", "value": male},
            ]

            result = db.execute(
                text(
                    f"SELECT race, COUNT(*) AS patient_count FROM {patient_table} GROUP BY race"
                )
            ).mappings().all()
            response_data["raceCategory"] = [
                {"category": row["race"], "value": row["patient_count"]} for row in result
            ]

            result = db.execute(
                text(
                    f"SELECT ethnicity, COUNT(*) AS patient_count FROM {patient_table} "
                    f"GROUP BY ethnicity"
                )
            ).mappings().all()
            response_data["ethnicityCategory"] = [
                {"category": row["ethnicity"], "value": row["patient_count"]}
                for row in result
            ]

            # Placeholder demo slices until dedicated columns are wired for these widgets.
            response_data["adjuvantTherapy"] = [
                {"category": "NA", "value": 100},
                {"category": "Yes", "value": 90},
                {"category": "No", "value": 30},
            ]

            result = db.execute(
                text(
                    f"SELECT PHARMACEUTICAL_TX_ADJUVANT, COUNT(*) AS patient_count "
                    f"FROM {patient_table} GROUP BY PHARMACEUTICAL_TX_ADJUVANT"
                )
            ).mappings().all()
            response_data["ajccMetastasis"] = [
                {
                    "category": row["PHARMACEUTICAL_TX_ADJUVANT"],
                    "value": row["patient_count"],
                }
                for row in result
            ]

            result = db.execute(
                text(
                    f"SELECT AJCC_METASTASIS_PATHOLOGIC_PM, COUNT(*) AS patient_count "
                    f"FROM {patient_table} GROUP BY AJCC_METASTASIS_PATHOLOGIC_PM"
                )
            ).mappings().all()
            response_data["ajccPublication"] = [
                {
                    "category": row["AJCC_METASTASIS_PATHOLOGIC_PM"],
                    "value": row["patient_count"],
                }
                for row in result
            ]

            result = db.execute(
                text(
                    f"SELECT AJCC_STAGING_EDITION, COUNT(*) AS patient_count "
                    f"FROM {patient_table} GROUP BY AJCC_STAGING_EDITION"
                )
            ).mappings().all()
            response_data["ajccTumor"] = [
                {
                    "category": row["AJCC_STAGING_EDITION"],
                    "value": row["patient_count"],
                }
                for row in result
            ]

            # ===== TABLES =====

            result = db.execute(text("SHOW TABLES")).fetchall()
            table_names = [row[0] for row in result]
            filtered_tables = [
                t
                for t in table_names
                if not any(ex in t for ex in ["meta", "cases", "sample", "patient"])
                and t.startswith(study)
            ]

            rep = {study: "", "data": "", "_": " "}
            table_new = [
                re.sub("|".join(rep.keys()), lambda m: rep[m.group()], t)
                for t in filtered_tables
            ]

            response_data["genomicProfile"] = {
                "columns": ["Molecular Profile", "# (Count)", "Frequency (%)"],
                "rows": [],
            }

            total_gp_rows = 0
            table_data = []
            for table, t in zip(filtered_tables, table_new):
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                row_count = count_result[0] if count_result else 0
                total_gp_rows += row_count
                table_data.append({"Molecular Profile": t.strip(), "# (Count)": row_count})

            for entry in table_data:
                entry["Frequency (%)"] = f"{round((entry['# (Count)'] / total_gp_rows) * 100, 1) if total_gp_rows > 0 else 0}"
                response_data["genomicProfile"]["rows"].append(entry)

            result = db.execute(
                text(
                    f"SELECT cancer_type_detailed, COUNT(*) AS cancer_type "
                    f"FROM {sample_table} GROUP BY cancer_type_detailed"
                )
            ).mappings().all()
            response_data["cancerTypeDetailed"] = {
                "columns": ["Category", "# (Number of Samples)", "Frequency (%)"],
                "rows": [],
            }
            total_samples = sum(row["cancer_type"] for row in result)
            for row in result:
                frequency = (row["cancer_type"] / total_samples) * 100 if total_samples else 0
                response_data["cancerTypeDetailed"]["rows"].append(
                    {
                        "Category": row["cancer_type_detailed"],
                        "# (Number of Samples)": row["cancer_type"],
                        "Frequency (%)": f"{frequency:.1f}",
                    }
                )

            result = db.execute(
                text(
                    f"SELECT hugo_symbol, COUNT(*) AS occurrence_count FROM {mutations_table} "
                    f"GROUP BY hugo_symbol ORDER BY occurrence_count DESC LIMIT 50"
                )
            ).mappings().all()
            total_mutations = sum(row["occurrence_count"] for row in result)
            response_data["mutatedGenes"] = {
                "columns": ["Gene", "Mutation (Mut)", "# (Count)", "Frequency (%)"],
                "rows": [],
            }

            def get_mutation_type(_gene):
                return "Missense"

            for row in result:
                frequency = (
                    (row["occurrence_count"] / total_mutations) * 100
                    if total_mutations
                    else 0
                )
                mutation_type = get_mutation_type(row["hugo_symbol"])
                response_data["mutatedGenes"]["rows"].append(
                    {
                        "Gene": row["hugo_symbol"],
                        "Mutation (Mut)": mutation_type,
                        "# (Count)": row["occurrence_count"],
                        "Frequency (%)": f"{frequency:.1f}",
                    }
                )

            # Global CNA rollup table in this schema (not study-prefixed); see query.sql.
            result = db.execute(
                text(
                    "SELECT gene, cytoband, CNA, num, freq FROM cna_gene ORDER BY num DESC LIMIT 100"
                )
            ).mappings().all()
            response_data["cnaGenes"] = {
                "columns": ["Gene Cytoband", "CNA", "# (Count)", "Frequency (%)"],
                "rows": [],
            }
            for row in result:
                response_data["cnaGenes"]["rows"].append(
                    {
                        "Gene Cytoband": f"{row['gene']} {row['cytoband']}",
                        "CNA": row["CNA"],
                        "# (Count)": row["num"],
                        "Frequency (%)": f"{row['freq']:.1f}",
                    }
                )

            response_data["brachytherapy"] = {
                "columns": ["Category", "# (Count)", "Frequency (%)"],
                "rows": [
                    {"Category": "NA", "# (Count)": 180, "Frequency (%)": "81.8"},
                    {"Category": "40-50 Gy", "# (Count)": 25, "Frequency (%)": "11.4"},
                    {"Category": "30-40 Gy", "# (Count)": 15, "Frequency (%)": "6.8"},
                ],
            }

            response_data["cent17CopyNumber"] = {
                "columns": ["Category", "# (Count)", "Frequency (%)"],
                "rows": [
                    {"Category": "NA", "# (Count)": 160, "Frequency (%)": "72.7"},
                    {"Category": "2", "# (Count)": 30, "Frequency (%)": "13.6"},
                    {"Category": "3", "# (Count)": 20, "Frequency (%)": "9.1"},
                    {"Category": "4+", "# (Count)": 10, "Frequency (%)": "4.5"},
                ],
            }

            # ===== BAR CHARTS =====

            bucket_row = db.execute(
                text(
                    f"""
                    SELECT
                        SUM(CASE WHEN gene_count BETWEEN 1 AND 10 THEN 1 ELSE 0 END) AS c_0_10,
                        SUM(CASE WHEN gene_count BETWEEN 11 AND 20 THEN 1 ELSE 0 END) AS c_11_20,
                        SUM(CASE WHEN gene_count BETWEEN 21 AND 30 THEN 1 ELSE 0 END) AS c_21_30,
                        SUM(CASE WHEN gene_count BETWEEN 31 AND 40 THEN 1 ELSE 0 END) AS c_31_40,
                        SUM(CASE WHEN gene_count >= 41 THEN 1 ELSE 0 END) AS c_41_plus
                    FROM (
                        SELECT COUNT(*) AS gene_count
                        FROM {mutations_table}
                        GROUP BY hugo_symbol
                    ) AS gene_counts
                    """
                )
            ).mappings().first()
            response_data["mutationCount"] = [
                {"range": "0-10", "count": int(bucket_row["c_0_10"] or 0)},
                {"range": "11-20", "count": int(bucket_row["c_11_20"] or 0)},
                {"range": "21-30", "count": int(bucket_row["c_21_30"] or 0)},
                {"range": "31-40", "count": int(bucket_row["c_31_40"] or 0)},
                {"range": "41+", "count": int(bucket_row["c_41_plus"] or 0)},
            ]

            result = db.execute(
                text(
                    f"SELECT n_genes_in_region, n_genes_in_peak FROM {gistic_table}"
                )
            ).mappings().all()
            range_counts = {f"{i / 10}-{(i + 1) / 10}": 0 for i in range(10)}
            for row in result:
                if row["n_genes_in_region"] > 0:
                    fraction = row["n_genes_in_peak"] / row["n_genes_in_region"]
                    for i in range(10):
                        lower_bound = i / 10
                        upper_bound = (i + 1) / 10
                        if lower_bound <= fraction < upper_bound:
                            range_counts[f"{lower_bound}-{upper_bound}"] += 1
                            break
            response_data["fractionGenomicAltered"] = [
                {"range": range_key, "count": count}
                for range_key, count in range_counts.items()
            ]

            result = db.execute(
                text(
                    f"SELECT days_to_birth FROM {patient_table} "
                    f"where days_to_birth <> '[Not Available]'"
                )
            ).mappings().all()
            days = [int(row["days_to_birth"]) for row in result]
            min_days = min(days)
            max_days = max(days)
            range_step = (max_days - min_days) / 6
            range_counts = {
                f"{int(min_days + i * range_step)}-{int(min_days + (i + 1) * range_step)}": 0
                for i in range(5)
            }
            range_counts[f"{int(min_days + 5 * range_step)}+"] = 0
            for day in days:
                for i in range(5):
                    lower_bound = min_days + i * range_step
                    upper_bound = min_days + (i + 1) * range_step
                    if lower_bound <= day < upper_bound:
                        range_counts[
                            f"{int(lower_bound)}-{int(upper_bound)}"
                        ] += 1
                        break
                else:
                    range_counts[f"{int(min_days + 5 * range_step)}+"] += 1
            response_data["birthFromDiagnosis"] = [
                {"range": range_key, "count": count}
                for range_key, count in range_counts.items()
            ]

            result = db.execute(
                text(
                    f"SELECT days_to_last_followup FROM {patient_table} "
                    f"where days_to_last_followup <> '[Not Available]'"
                )
            ).mappings().all()
            followup_days = [int(row["days_to_last_followup"]) for row in result]
            min_days = min(followup_days)
            max_days = max(followup_days)
            range_step = (max_days - min_days) / 6
            range_counts = {
                f"{int(min_days + i * range_step)}-{int(min_days + (i + 1) * range_step)}": 0
                for i in range(5)
            }
            range_counts[f"{int(min_days + 5 * range_step)}+"] = 0
            for day in followup_days:
                for i in range(5):
                    lower_bound = min_days + i * range_step
                    upper_bound = min_days + (i + 1) * range_step
                    if lower_bound <= day < upper_bound:
                        range_counts[
                            f"{int(lower_bound)}-{int(upper_bound)}"
                        ] += 1
                        break
                else:
                    range_counts[f"{int(min_days + 5 * range_step)}+"] += 1
            response_data["daysToFollowup"] = [
                {"range": range_key, "count": count}
                for range_key, count in range_counts.items()
            ]

            result = db.execute(
                text(
                    f"SELECT days_to_collection FROM {sample_table} "
                    f"where days_to_collection <> '[Not Available]'"
                )
            ).mappings().all()
            collection_days = [int(row["days_to_collection"]) for row in result]
            quantiles = np.quantile(collection_days, [0, 0.2, 0.4, 0.6, 0.8, 1.0])
            range_counts = {
                f"{int(quantiles[i])}-{int(quantiles[i + 1])}": 0
                for i in range(len(quantiles) - 1)
            }
            for day in collection_days:
                for i in range(len(quantiles) - 1):
                    lower_bound = quantiles[i]
                    upper_bound = quantiles[i + 1]
                    if lower_bound <= day < upper_bound:
                        range_counts[
                            f"{int(lower_bound)}-{int(upper_bound)}"
                        ] += 1
                        break
            response_data["daysToCollection"] = [
                {"range": range_key, "count": count}
                for range_key, count in range_counts.items()
            ]

            result = db.execute(
                text(
                    f"SELECT days_to_death FROM {patient_table} "
                    f"WHERE days_to_death <> '[NOT Applicable]'"
                )
            ).mappings().all()
            death_days = [int(row["days_to_death"]) for row in result]
            quantiles = np.quantile(death_days, [0, 0.2, 0.4, 0.6, 0.8, 1.0])
            range_counts = {
                f"{int(quantiles[i])}-{int(quantiles[i + 1])}": 0
                for i in range(len(quantiles) - 1)
            }
            for day in death_days:
                for i in range(len(quantiles) - 1):
                    lower_bound = quantiles[i]
                    upper_bound = quantiles[i + 1]
                    if lower_bound <= day < upper_bound:
                        range_counts[
                            f"{int(lower_bound)}-{int(upper_bound)}"
                        ] += 1
                        break
            response_data["deathFromDiagnosis"] = [
                {"range": range_key, "count": count}
                for range_key, count in range_counts.items()
            ]

            result = db.execute(
                text(
                    f"""
                    SELECT t_ref_count, t_alt_count
                    FROM {mutations_table}
                    WHERE t_ref_count > 0
                      AND t_alt_count > 0
                      AND t_alt_count / t_ref_count < 1
                    LIMIT 100
                    """
                )
            ).mappings().all()
            response_data["mutationVsFraction"] = []
            for row in result:
                t_ref_count = row["t_ref_count"]
                t_alt_count = row["t_alt_count"]
                fraction_genome_altered = t_alt_count / t_ref_count
                response_data["mutationVsFraction"].append(
                    {
                        "mutationCount": t_ref_count,
                        "fractionGenomeAltered": fraction_genome_altered,
                    }
                )

            result = db.execute(
                text(
                    f"SELECT os_months, os_status FROM {patient_table} "
                    f"WHERE os_months NOT LIKE '%Not Available%'"
                )
            ).mappings().all()
            df = pd.DataFrame(result)
            df["event"] = df["os_status"].apply(lambda x: 1 if x == "1:DECEASED" else 0)
            kmf = KaplanMeierFitter()
            kmf.fit(durations=df["os_months"], event_observed=df["event"])
            response_data["kmOverall"] = []
            for time, survival_prob in zip(
                kmf.survival_function_.index,
                kmf.survival_function_["KM_estimate"],
            ):
                censored = not df[df["os_months"] == time]["event"].any()
                response_data["kmOverall"].append(
                    {
                        "time": time,
                        "survival": survival_prob,
                        "censored": censored,
                    }
                )

            result = db.execute(
                text(
                    f"SELECT dfs_months, dfs_status FROM {patient_table} "
                    f"WHERE dfs_months NOT LIKE '%Not Available%'"
                )
            ).mappings().all()
            df_dfs = pd.DataFrame(result)
            df_dfs["event"] = df_dfs["dfs_status"].apply(
                lambda x: 1 if x == "1:Recurred/Progressed" else 0
            )
            kmf_dfs = KaplanMeierFitter()
            kmf_dfs.fit(durations=df_dfs["dfs_months"], event_observed=df_dfs["event"])
            response_data["kmDiseaseFree"] = []
            for time, survival_prob in zip(
                kmf_dfs.survival_function_.index,
                kmf_dfs.survival_function_["KM_estimate"],
            ):
                censored = not df_dfs[df_dfs["dfs_months"] == time]["event"].any()
                response_data["kmDiseaseFree"].append(
                    {
                        "time": time,
                        "survival": survival_prob,
                        "censored": censored,
                    }
                )

            cache_service.set_json("summary", cache_key, response_data)
            return response_data, HTTPStatus.OK

        except Exception:
            return internal_error_response(
                f"GET /summary/{dataset_name} failed",
            ), HTTPStatus.INTERNAL_SERVER_ERROR
