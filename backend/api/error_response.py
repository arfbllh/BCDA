def api_error(code, message, request_id=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

