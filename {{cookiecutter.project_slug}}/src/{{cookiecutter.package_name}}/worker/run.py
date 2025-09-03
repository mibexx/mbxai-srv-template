#!/usr/bin/env python3
"""Celery worker entry point for {{cookiecutter.package_name}}."""

import logging
import sys

from .tasks import celery_app


def main() -> None:
    """Main entry point for the Celery worker."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting {{cookiecutter.package_name}} Celery worker...")

    # Start the worker with basic configuration
    worker = celery_app.Worker(loglevel="info")
    worker.start()


if __name__ == "__main__":
    main()
