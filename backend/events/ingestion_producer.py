"""Publish ingestion lifecycle events to Kafka when KAFKA_ENABLED is set."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from core.config import get_config

logger = logging.getLogger(__name__)

_producer = None


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _kafka_enabled() -> bool:
    cfg = get_config()
    return bool(cfg.KAFKA_ENABLED and cfg.KAFKA_BOOTSTRAP_SERVERS.strip())


def _get_producer():
    global _producer
    if not _kafka_enabled():
        return None
    if _producer is not None:
        return _producer
    try:
        from kafka import KafkaProducer

        cfg = get_config()
        servers = [s.strip() for s in cfg.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]
        _producer = KafkaProducer(
            bootstrap_servers=servers,
            client_id=cfg.KAFKA_CLIENT_ID,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: (k.encode("utf-8") if k is not None else None),
            retries=3,
            acks="all",
        )
        return _producer
    except Exception as exc:
        logger.warning("Kafka producer initialization failed: %s", exc)
        return None


def _send_dlq(original_envelope: dict, error_message: str) -> None:
    cfg = get_config()
    producer = _get_producer()
    if producer is None:
        logger.error("ingestion DLQ skipped (no producer): %s", error_message)
        return
    dlq_payload = {
        "event_type": "ingestion.delivery_failed",
        "occurred_at": _utc_iso(),
        "error": error_message,
        "original": original_envelope,
    }
    try:
        producer.send(cfg.KAFKA_DLQ_TOPIC, value=dlq_payload)
        producer.flush(timeout=8)
    except Exception as exc:
        logger.error("ingestion DLQ publish failed: %s", exc)


def publish_ingestion_event(
    event_type: str,
    dataset_name: str,
    *,
    run_id: str | None = None,
    extra: dict | None = None,
) -> None:
    """Best-effort publish; failures go to DLQ when the producer is available."""
    if not _kafka_enabled():
        return
    producer = _get_producer()
    if producer is None:
        return

    cfg = get_config()
    envelope = {
        "event_type": event_type,
        "occurred_at": _utc_iso(),
        "dataset_name": dataset_name,
        "run_id": run_id,
    }
    if extra:
        envelope["payload"] = extra

    key = dataset_name or "unknown"
    try:
        producer.send(cfg.KAFKA_INGESTION_TOPIC, key=key, value=envelope)
        producer.flush(timeout=12)
    except Exception as exc:
        logger.error("Kafka ingestion event publish failed: %s", exc)
        _send_dlq(envelope, str(exc))


def flush_producer() -> None:
    """Flush pending messages (e.g. before process exit)."""
    global _producer
    if _producer is not None:
        try:
            _producer.flush(timeout=15)
        except Exception as exc:
            logger.warning("Kafka producer flush failed: %s", exc)
