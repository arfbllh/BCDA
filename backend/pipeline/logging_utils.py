import logging
import os
import sys


def get_pipeline_logger():
    """Create logger for ingestion pipeline."""
    os.makedirs("./logs", exist_ok=True)
    logger = logging.getLogger("data_loader")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler = logging.FileHandler("./logs/data_loader.log")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

