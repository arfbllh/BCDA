"""seed studies catalog when empty (dev-friendly)

Revision ID: 20260421_000003
Revises: 20260421_000002
Create Date: 2026-04-21 00:00:03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260421_000003"
down_revision = "20260421_000002"
branch_labels = None
depends_on = None

# Matches legacy utils/init_db.py seed list (study_id == display name for routing).
_SEED = [
    ("brca_tcga_pub2015", "Invasive Breast Carcinoma", "brca_tcga_pub2015"),
    ("brca_tcga", "Invasive Breast Carcinoma", "brca_tcga"),
    ("brca_tcga_pan_can_atlas_2018", "Invasive Breast Carcinoma", "brca_tcga_pan_can_atlas_2018"),
    ("brca_tcga_pub", "Invasive Breast Carcinoma", "brca_tcga_pub"),
    ("brca_tcga_gdc", "Invasive Breast Carcinoma", "brca_tcga_gdc"),
    ("breast_cptac_gdc", "Breast", "breast_cptac_gdc"),
    ("bfn_duke_nus_2015", "Breast Fibroepithelial Neoplasms", "bfn_duke_nus_2015"),
    ("mbc_msk_2021", "Metaplastic Breast Cancer", "mbc_msk_2021"),
]


def upgrade():
    conn = op.get_bind()
    count = conn.execute(sa.text("SELECT COUNT(*) FROM studies")).scalar_one()
    if count > 0:
        return
    insert = sa.text(
        """
        INSERT INTO studies (
            study_id, type_of_cancer, name, is_active, created_at, updated_at
        ) VALUES (
            :study_id, :type_of_cancer, :name, 1, UTC_TIMESTAMP(), UTC_TIMESTAMP()
        )
        """
    )
    for study_id, type_of_cancer, name in _SEED:
        conn.execute(
            insert,
            {"study_id": study_id, "type_of_cancer": type_of_cancer, "name": name},
        )


def downgrade():
    conn = op.get_bind()
    for study_id, _, _ in _SEED:
        conn.execute(sa.text("DELETE FROM studies WHERE study_id = :sid"), {"sid": study_id})
