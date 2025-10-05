#!/usr/bin/env python3
"""Celery worker entry point for web_scraper."""

import logging
import sys

from .tasks import celery_app
from ..config import get_celery_config
from ..utils import get_celery_client


def main() -> None:
    """Main entry point for the Celery worker."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logger = logging.getLogger(__name__)
    
    # Get Celery configuration
    celery_config = get_celery_config()
    worker_name = celery_config.worker_name
    queue_name = celery_config.task_prefix  # Use task_prefix as queue name
    
    # Get the celery client to access the configured queue
    celery_client = get_celery_client()
    default_queue = celery_client.default_queue
    
    logger.info(f"Starting web_scraper Celery worker with name: {worker_name}")
    logger.info(f"Configured task prefix: {queue_name}")
    logger.info(f"Worker will listen to dedicated queue: {default_queue}")
    logger.info("This prevents cross-service task pollution and message loss")
    
    # Verify they match
    if default_queue != queue_name:
        logger.warning(f"Queue mismatch! Expected: {queue_name}, Got: {default_queue}")

    # Start the worker with configured hostname and dedicated queue
    worker = celery_app.Worker(
        loglevel="info", 
        hostname=worker_name,
        queues=[default_queue]
    )
    worker.start()


if __name__ == "__main__":
    main()
