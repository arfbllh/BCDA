import json
import logging
import time
import uuid

from flask import g, request


logger = logging.getLogger("platform.request")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def init_request_context(app):
    @app.before_request
    def _set_request_id():
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_id = request_id
        g.request_start_ts = time.time()

    @app.after_request
    def _attach_request_id(response):
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers["X-Request-ID"] = request_id

        started = getattr(g, "request_start_ts", None)
        duration_ms = None
        if started is not None:
            duration_ms = int((time.time() - started) * 1000)

        log_payload = {
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
        logger.info(json.dumps(log_payload))
        return response

