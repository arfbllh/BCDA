"""create core platform tables

Revision ID: 20260421_000001
Revises:
Create Date: 2026-04-21 00:00:01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260421_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=False),
        sa.Column("study_id", sa.String(length=128), nullable=False),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("request_payload", sa.Text(), nullable=True),
        sa.Column("result_payload", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("queued_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_jobs_job_id"), "analysis_jobs", ["job_id"], unique=True)
    op.create_index(op.f("ix_analysis_jobs_job_type"), "analysis_jobs", ["job_type"], unique=False)
    op.create_index(op.f("ix_analysis_jobs_status"), "analysis_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_analysis_jobs_study_id"), "analysis_jobs", ["study_id"], unique=False)

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("study_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("row_counts_json", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_runs_run_id"), "ingestion_runs", ["run_id"], unique=True)
    op.create_index(op.f("ix_ingestion_runs_status"), "ingestion_runs", ["status"], unique=False)
    op.create_index(op.f("ix_ingestion_runs_study_id"), "ingestion_runs", ["study_id"], unique=False)

    op.create_table(
        "studies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.String(length=128), nullable=False),
        sa.Column("type_of_cancer", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("citation", sa.String(length=255), nullable=True),
        sa.Column("pmid", sa.String(length=32), nullable=True),
        sa.Column("source", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_studies_study_id"), "studies", ["study_id"], unique=True)
    op.create_index(op.f("ix_studies_type_of_cancer"), "studies", ["type_of_cancer"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_studies_type_of_cancer"), table_name="studies")
    op.drop_index(op.f("ix_studies_study_id"), table_name="studies")
    op.drop_table("studies")

    op.drop_index(op.f("ix_ingestion_runs_study_id"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_status"), table_name="ingestion_runs")
    op.drop_index(op.f("ix_ingestion_runs_run_id"), table_name="ingestion_runs")
    op.drop_table("ingestion_runs")

    op.drop_index(op.f("ix_analysis_jobs_study_id"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_status"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_job_type"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_job_id"), table_name="analysis_jobs")
    op.drop_table("analysis_jobs")

