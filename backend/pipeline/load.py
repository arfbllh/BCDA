
import pandas as pd
from sqlalchemy import Boolean, Column, Float, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from sqlalchemy_utils import database_exists

from pipeline.transform import sanitize_column_name


def get_engine_from_config(config, logger):
    db_url = (
        f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
        f"@{config.MYSQL_HOST}/{config.MYSQL_DB}"
    )
    root_url = (
        f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
        f"@{config.MYSQL_HOST}/"
    )
    temp_engine = create_engine(root_url)
    if not database_exists(db_url):
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB}"))
        logger.info("Created database: %s", config.MYSQL_DB)
    return create_engine(db_url)


def create_dynamic_table(table_name, df, metadata):
    table_columns = [Column("id", Integer, primary_key=True, autoincrement=True)]
    df.columns = [sanitize_column_name(col) for col in df.columns]

    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            col_type = Integer
        elif pd.api.types.is_float_dtype(dtype):
            col_type = Float
        elif pd.api.types.is_bool_dtype(dtype):
            col_type = Boolean
        else:
            max_len = df[col].astype(str).str.len().max()
            max_len = int(max_len) if pd.notna(max_len) else 255
            col_type = Text if max_len > 255 else String(max(255, max_len))
        table_columns.append(Column(col, col_type))

    return Table(table_name, metadata, *table_columns)


def load_dataframe_to_table(engine, df, table_name, logger):
    try:
        df.columns = [sanitize_column_name(col) for col in df.columns]
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
        )
        logger.info("Loaded %s rows into %s", len(df.index), table_name)
        return True
    except SQLAlchemyError as exc:
        logger.error("Failed to load %s: %s", table_name, exc)
        return False


def load_single_table(engine, table_name, df, logger):
    if df is None or df.empty:
        logger.warning("Skipping empty table payload for %s", table_name)
        return False
    metadata = MetaData()
    table = create_dynamic_table(table_name, df, metadata)
    table.metadata.create_all(engine)
    return load_dataframe_to_table(engine, df, table_name, logger)

