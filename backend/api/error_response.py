"""Standard JSON error body for non-2xx API responses (see doc/api-contract.md)."""

import logging

logger = logging.getLogger(__name__)


def api_error(code, message, request_id=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }


def internal_error_response(log_message: str):
    """Safe 500 JSON body; log with traceback (call from an ``except`` block)."""
    logger.exception(log_message)
    return api_error(
        "INTERNAL_ERROR",
        "Something went wrong on the server. Please try again later.",
    )


def format_pydantic_errors(errors) -> str:
    """Short human-readable summary for API clients (not raw Pydantic JSON)."""
    if not isinstance(errors, list) or not errors:
        return "Validation failed."
    parts = []
    for err in errors[:10]:
        if not isinstance(err, dict):
            parts.append(str(err))
            continue
        loc = err.get("loc") or ()
        tail = [str(x) for x in loc if str(x) not in ("body", "json", "query")]
        ctx = ".".join(tail) if tail else "field"
        parts.append(f"{ctx}: {err.get('msg', 'invalid')}")
    return "; ".join(parts)

