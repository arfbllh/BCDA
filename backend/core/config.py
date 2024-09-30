"""Environment-based application configuration."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    _BACKEND_ROOT = Path(__file__).resolve().parents[1]
    _REPO_ROOT = _BACKEND_ROOT.parent
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(_BACKEND_ROOT / ".env")
except ImportError:
    pass

from sqlalchemy.pool import StaticPool


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_for_development")
    DEBUG = False
    TESTING = False
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "20"))
    API_MAX_CLINICAL_ROWS = int(os.getenv("API_MAX_CLINICAL_ROWS", "500"))
    API_CLINICAL_DEFAULT_LIMIT = int(os.getenv("API_CLINICAL_DEFAULT_LIMIT", "200"))

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "cancer_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600")),
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10")),
    }

    SQLALCHEMY_ECHO = _as_bool(os.getenv("SQLALCHEMY_ECHO"), False)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    _BACKEND_ROOT = Path(__file__).resolve().parents[1]
    _REPO_ROOT = _BACKEND_ROOT.parent
    # Raw study bundles (cBioPortal-style) for ingestion and on-demand CSV reads.
    _datasets_rel = os.getenv("DATASETS_BASE_DIR", "datasets")
    _datasets_path = Path(_datasets_rel)
    DATASETS_BASE_DIR = (
        str(_datasets_path.resolve())
        if _datasets_path.is_absolute()
        else str((_BACKEND_ROOT / _datasets_path).resolve())
    )
    MATRIX_STORAGE_DIR = os.getenv("MATRIX_STORAGE_DIR", "./storage/matrix")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TASK_ALWAYS_EAGER = _as_bool(os.getenv("CELERY_TASK_ALWAYS_EAGER"), False)
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    KAFKA_ENABLED = _as_bool(os.getenv("KAFKA_ENABLED"), False)
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
    KAFKA_INGESTION_TOPIC = os.getenv("KAFKA_INGESTION_TOPIC", "ingestion.events")
    KAFKA_DLQ_TOPIC = os.getenv("KAFKA_DLQ_TOPIC", "ingestion.dlq")
    KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "bcancerportal-ingestion")

    # Optional OpenAI-compatible LLM (Ollama, vLLM, OpenAI, etc.) — see ADR-0007.
    LLM_INFERENCE_ENABLED = _as_bool(os.getenv("LLM_INFERENCE_ENABLED"), False)
    LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "512"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
    # Single shared in-memory DB for API + eager Celery tasks (avoids empty connections).
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SQLALCHEMY_ECHO = False
    CELERY_TASK_ALWAYS_EAGER = True
    CACHE_TTL_SECONDS = 5
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

