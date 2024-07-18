"""Environment-based application configuration."""

import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_for_development")
    DEBUG = False
    TESTING = False
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "20"))

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "cancer_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = _as_bool(os.getenv("SQLALCHEMY_ECHO"), False)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    MYSQL_DB = os.getenv("MYSQL_DB_TEST", "cancer_db_test")


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config(env_name=None):
    env = (env_name or os.getenv("APP_ENV", "development")).strip().lower()
    mapping = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
    }
    return mapping.get(env, DevelopmentConfig)

