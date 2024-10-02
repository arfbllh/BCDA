Local cBioPortal-style bundles (two studies example)
===================================================

The API catalog (GET /api/v1/datasets) reads MySQL table `studies`. Clinical,
summary, and heatmap expect files under DATASETS_BASE_DIR (default: backend/datasets)
and — for SQL-backed tabs — tables created by ingestion.

1) Create the data directory (backend/datasets is gitignored; it will not appear in git):

   mkdir -p backend/datasets

2) Copy this index and edit the `name` column to match YOUR folder names (one row per study):

   cp backend/datasets.example/datasets.csv backend/datasets/datasets.csv

3) For each `name` value, add a folder:

   backend/datasets/<name>/

   with cBioPortal-style files (examples: data_clinical_patient.txt, data_clinical_sample.txt,
   data_mutations.txt, data_gistic_genes_amp.txt, data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv, …).

   The URL path /api/v1/datasets/<name>/... uses the same string as `name` and as `studies.study_id`.

4) Ensure each study appears in MySQL `studies` with is_active=1. The seed migration inserts
   common TCGA ids (e.g. brca_tcga_pub2015, brca_tcga). For custom ids, INSERT a row yourself.

5) From backend/, with MySQL running and migrations applied:

   python dataloader.py

6) Optional — if the UI lists studies you did not ingest, hide them:

   UPDATE studies SET is_active = 0 WHERE study_id NOT IN ('study_a','study_b');

7) If bundles live outside the repo, set in .env:

   DATASETS_BASE_DIR=/absolute/path/to/parent/of/study/folders

   That directory must still contain datasets.csv and one subfolder per name.

Verify: GET /api/v1/datasets/<name>/data-status
