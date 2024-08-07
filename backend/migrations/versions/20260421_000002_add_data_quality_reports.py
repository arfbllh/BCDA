"""add data quality reports table

Revision ID: 20260421_000002
Revises: 20260421_000001
Create Date: 2026-04-21 00:00:02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260421_000002"
down_revision = "20260421_000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "data_quality_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("study_id", sa.String(length=128), nullable=False),
        sa.Column("check_name", sa.String(length=128), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_data_quality_reports_run_id"),
        "data_quality_reports",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_data_quality_reports_study_id"),
        "data_quality_reports",
        ["study_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_data_quality_reports_check_name"),
        "data_quality_reports",
        ["check_name"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_data_quality_reports_check_name"), table_name="data_quality_reports")
    op.drop_index(op.f("ix_data_quality_reports_study_id"), table_name="data_quality_reports")
    op.drop_index(op.f("ix_data_quality_reports_run_id"), table_name="data_quality_reports")
    op.drop_table("data_quality_reports")

