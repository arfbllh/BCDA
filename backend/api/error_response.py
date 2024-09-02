"""Standard JSON error body for non-2xx API responses (see doc/api-contract.md)."""


def api_error(code, message, request_id=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

