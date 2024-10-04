"""add auth and upload tables

Revision ID: 20260422_000004
Revises: 20260421_000003
Create Date: 2026-04-22 00:00:04
"""

from alembic import op
import sqlalchemy as sa


revision = "20260422_000004"
down_revision = "20260421_000003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "invite_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=False),
        sa.Column("used_count", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invite_codes_code"), "invite_codes", ["code"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_sessions_token"), "auth_sessions", ["token"], unique=True)
    op.create_index(op.f("ix_auth_sessions_user_id"), "auth_sessions", ["user_id"], unique=False)

    op.create_table(
        "upload_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("upload_id", sa.String(length=64), nullable=False),
        sa.Column("study_id", sa.String(length=128), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("ingestion_run_id", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_upload_submissions_upload_id"), "upload_submissions", ["upload_id"], unique=True)
    op.create_index(op.f("ix_upload_submissions_study_id"), "upload_submissions", ["study_id"], unique=False)
    op.create_index(op.f("ix_upload_submissions_status"), "upload_submissions", ["status"], unique=False)

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO invite_codes (
                code, description, max_uses, used_count, is_active, expires_at, created_at, updated_at
            ) VALUES (
                'BCP-INVITE-2024',
                'Default development invite code',
                100,
                0,
                1,
                DATE_ADD(UTC_TIMESTAMP(), INTERVAL 365 DAY),
                UTC_TIMESTAMP(),
                UTC_TIMESTAMP()
            )
            """
        )
    )


def downgrade():
    op.drop_index(op.f("ix_upload_submissions_status"), table_name="upload_submissions")
    op.drop_index(op.f("ix_upload_submissions_study_id"), table_name="upload_submissions")
    op.drop_index(op.f("ix_upload_submissions_upload_id"), table_name="upload_submissions")
    op.drop_table("upload_submissions")

    op.drop_index(op.f("ix_auth_sessions_user_id"), table_name="auth_sessions")
    op.drop_index(op.f("ix_auth_sessions_token"), table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index(op.f("ix_invite_codes_code"), table_name="invite_codes")
    op.drop_table("invite_codes")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
