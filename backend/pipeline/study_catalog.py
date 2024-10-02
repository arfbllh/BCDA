"""Register or refresh catalog rows in ``studies`` after successful ingestion."""

from sqlalchemy import text


def upsert_study_catalog_entry(
    engine,
    study_id: str,
    *,
    type_of_cancer: str = "Breast",
    display_name: str | None = None,
):
    """Ensure ``studies`` has an active row for ``study_id`` (MySQL pipeline engine)."""
    name = display_name or study_id
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT id FROM studies WHERE study_id = :sid"),
            {"sid": study_id},
        ).first()
        if row:
            conn.execute(
                text(
                    """
                    UPDATE studies
                    SET is_active = 1,
                        name = :name,
                        type_of_cancer = :toc,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE study_id = :sid
                    """
                ),
                {"sid": study_id, "name": name, "toc": type_of_cancer},
            )
        else:
            conn.execute(
                text(
                    """
                    INSERT INTO studies (
                        study_id, type_of_cancer, name, is_active, created_at, updated_at
                    ) VALUES (
                        :sid, :toc, :name, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    """
                ),
                {"sid": study_id, "toc": type_of_cancer, "name": name},
            )
