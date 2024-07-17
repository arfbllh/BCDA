import os
from core.config import get_config


_active_config = get_config(os.getenv("APP_ENV", "development"))


class Config(_active_config):
    """Backward-compatible config alias for existing imports."""