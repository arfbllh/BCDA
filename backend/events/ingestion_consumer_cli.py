"""
Minimal consumer for ingestion topics (monitoring / debugging).

Usage (from repo root, with Kafka up):
  PYTHONPATH=backend python -m events.ingestion_consumer_cli

Check consumer lag (example, image-dependent):
  kafka-consumer-groups.sh --bootstrap-server localhost:9092 \\
    --describe --group bcancerportal-ingestion-monitor
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consume ingestion Kafka topics")
    parser.add_argument(
        "--bootstrap",
        default="localhost:9092",
        help="Comma-separated broker list",
    )
    parser.add_argument(
        "--topic",
        default="ingestion.events",
        help="Primary topic to read",
    )
    parser.add_argument(
        "--group",
        default="bcancerportal-ingestion-monitor",
        help="Consumer group id (used for lag metrics)",
    )
    args = parser.parse_args(argv)

    try:
        from kafka import KafkaConsumer
    except ImportError:
        logger.error("kafka-python is not installed")
        return 1

    servers = [s.strip() for s in args.bootstrap.split(",") if s.strip()]
    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=servers,
        group_id=args.group,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    logger.info("Listening on %s topic=%s group=%s", servers, args.topic, args.group)
    try:
        for message in consumer:
            logger.info("%s-%s %s", message.topic, message.partition, message.value)
    except KeyboardInterrupt:
        logger.info("Stopping consumer")
    finally:
        consumer.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
