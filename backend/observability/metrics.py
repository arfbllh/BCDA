import time

from flask import g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total HTTP 5xx responses",
    ["method", "endpoint"],
)


def init_metrics(app):
    @app.before_request
    def _start_timer():
        g._req_start = time.time()

    @app.after_request
    def _record_metrics(response):
        endpoint = request.endpoint or "unknown"
        method = request.method
        status_code = str(response.status_code)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        start = getattr(g, "_req_start", None)
        if start is not None:
            elapsed = max(time.time() - start, 0.0)
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)

        if response.status_code >= 500:
            REQUEST_ERRORS.labels(method=method, endpoint=endpoint).inc()
        return response

    @app.get("/metrics")
    def metrics():
        payload = generate_latest()
        return app.response_class(payload, mimetype=CONTENT_TYPE_LATEST)

