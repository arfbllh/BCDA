# BCancerPortal API / worker image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/matrix /app/logs

EXPOSE 4000

# Default: HTTP API (override in compose for worker)
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
