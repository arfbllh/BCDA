"""Shared request pagination helpers."""

from flask import request

from core.config import get_config


def clinical_list_params():
    """Parse limit/offset for clinical list endpoints; values are capped."""
    cfg = get_config()
    max_rows = cfg.API_MAX_CLINICAL_ROWS
    default_limit = min(cfg.API_CLINICAL_DEFAULT_LIMIT, max_rows)

    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int, default=0)

    if limit is None:
        limit = default_limit
    limit = max(1, min(int(limit), max_rows))
    offset = max(0, int(offset))

    return limit, offset
