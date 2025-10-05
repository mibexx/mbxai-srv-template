#!/usr/bin/env python3
"""Celery worker entry point for web_scraper."""

import logging
import sys

from .tasks import celery_app
from ..config import get_celery_config


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
    task_prefix = celery_config.task_prefix
    
    logger.info(f"Starting web_scraper Celery worker with name: {worker_name}")
    logger.info(f"Worker will only process tasks with prefix: {task_prefix}")
    logger.info("Worker will listen to default queue (shared with other services)")

    # Start the worker with configured hostname (using default queue)
    worker = celery_app.Worker(loglevel="info", hostname=worker_name)
    worker.start()


if __name__ == "__main__":
    main()
