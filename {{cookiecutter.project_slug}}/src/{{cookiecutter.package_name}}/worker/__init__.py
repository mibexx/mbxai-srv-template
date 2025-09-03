"""Celery worker module for {{cookiecutter.package_name}}."""

from .tasks import *  # noqa: F401, F403
from .run import main

__all__ = ["main"]
