from sqlalchemy import text


def table_row_count(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        return int(result or 0)


def verify_loaded_tables(engine, table_names, logger):
    summary = {}
    for table_name in table_names:
        try:
            summary[table_name] = table_row_count(engine, table_name)
        except Exception as exc:
            logger.warning("Verification failed for %s: %s", table_name, exc)
    return summary

