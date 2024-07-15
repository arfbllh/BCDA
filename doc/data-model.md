# Data Model (Logical)

## Modeling Principles
- Keep study/cancer type explicit for multi-study extensibility
- Separate dynamic clinical attributes from normalized entities
- Track ingestion lineage and data quality outputs

## Core Entities
- `studies`
  - `study_id` (PK), `type_of_cancer`, `name`, `citation`, `pmid`, `source`
- `patients`
  - `patient_id` (PK within study), `study_id` (FK), demographic and survival fields
- `samples`
  - `sample_id` (PK within study), `patient_id` (FK), `study_id` (FK), sample descriptors
- `mutations`
  - mutation-level rows keyed by `study_id` + `sample_id` + genomic fields

## Flexible Clinical Modeling
- `clinical_attributes`
  - Attribute dictionary per study (`attribute_id`, `display_name`, `datatype`, `level`)
- `clinical_values`
  - Key-value records for patient/sample clinical values

## Pipeline and Operational Entities
- `ingestion_runs`
  - `run_id`, `study_id`, `status`, `started_at`, `finished_at`, `checksum`, `row_counts_json`
- `ingestion_files`
  - per-file status, retry_count, error_message, parsed_schema_hash
- `data_quality_reports`
  - check results and details per run
- `analysis_jobs`
  - async job queue status and output references

## Matrix Data Layout (Parquet)
- Datasets: `mrna_expression`, `methylation`, `linear_cna`, `rppa`
- Partition keys:
  - `study_id`
  - optional `datatype`
  - optional `gene_bucket`
- Access pattern:
  - Slice by `study_id + gene/sample set`
  - Query using DuckDB/PyArrow from worker/api service

## Relationship Notes
- One study has many patients, samples, mutations, runs
- One patient has many samples
- One run has many ingestion files and quality checks
