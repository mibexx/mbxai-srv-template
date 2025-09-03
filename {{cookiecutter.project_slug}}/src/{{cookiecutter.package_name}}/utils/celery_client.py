"""Celery client for asynchronous job processing with RabbitMQ and Redis."""

import logging
from typing import Any
from functools import lru_cache

from celery import Celery
from celery.result import AsyncResult

from ..config import get_rabbitmq_config, get_redis_config, get_celery_config


logger = logging.getLogger(__name__)


class CeleryClient:
    """Client for sending and receiving messages through Celery with RabbitMQ and Redis."""

    def __init__(self, app_name: str = "{{cookiecutter.package_name}}"):
        """Initialize the Celery client.
        
        Args:
            app_name: Name of the Celery application
        """
        self.app_name = app_name
        self._app = None
        self._setup_celery()

    def _setup_celery(self) -> None:
        """Set up the Celery application with RabbitMQ and Redis configuration."""
        rabbitmq_config = get_rabbitmq_config()
        redis_config = get_redis_config()
        celery_config = get_celery_config()

        # Create Celery app
        self._app = Celery(self.app_name)

        # Configure Celery
        self._app.conf.update(
            broker_url=rabbitmq_config.broker_url,
            result_backend=redis_config.result_backend_url,
            task_serializer=celery_config.task_serializer,
            result_serializer=celery_config.result_serializer,
            accept_content=celery_config.accept_content,
            result_expires=celery_config.result_expires,
            timezone=celery_config.timezone,
            enable_utc=celery_config.enable_utc,
            task_track_started=celery_config.task_track_started,
            task_time_limit=celery_config.task_time_limit,
            task_soft_time_limit=celery_config.task_soft_time_limit,
        )

        logger.info(f"Celery configured with broker: {rabbitmq_config.broker_url}")
        logger.info(f"Celery configured with result backend: {redis_config.result_backend_url}")

    @property
    def app(self) -> Celery:
        """Get the Celery application instance."""
        if self._app is None:
            self._setup_celery()
        return self._app

    def send_task(
        self,
        task_name: str,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        queue: str | None = None,
        routing_key: str | None = None,
        **options: Any
    ) -> str:
        """Send a task to the message queue.
        
        Args:
            task_name: Name of the task to execute
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
            queue: Queue name to send the task to
            routing_key: Routing key for the task
            **options: Additional Celery send_task options
            
        Returns:
            Task ID for tracking the task result
            
        Example:
            task_id = client.send_task(
                'my_app.tasks.process_data',
                args=[1, 2, 3],
                kwargs={'option': 'value'}
            )
        """
        logger.info(f"Sending task '{task_name}' with args={args}, kwargs={kwargs}")
        
        send_options = {}
        if queue:
            send_options['queue'] = queue
        if routing_key:
            send_options['routing_key'] = routing_key
        send_options.update(options)

        result = self.app.send_task(
            task_name,
            args=args or (),
            kwargs=kwargs or {},
            **send_options
        )
        
        logger.info(f"Task '{task_name}' sent with ID: {result.id}")
        return result.id

    def get_task_result(self, task_id: str, timeout: float | None = None) -> Any:
        """Get the result of a task.
        
        Args:
            task_id: ID of the task
            timeout: Timeout in seconds to wait for the result
            
        Returns:
            The task result
            
        Raises:
            celery.exceptions.Retry: If the task is retrying
            Exception: If the task failed
            
        Example:
            result = client.get_task_result(task_id, timeout=30)
        """
        logger.info(f"Getting result for task: {task_id}")
        
        async_result = AsyncResult(task_id, app=self.app)
        
        if timeout is not None:
            result = async_result.get(timeout=timeout)
        else:
            result = async_result.get()
            
        logger.info(f"Task {task_id} completed with result type: {type(result)}")
        return result

    def get_task_status(self, task_id: str) -> str:
        """Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
            
        Example:
            status = client.get_task_status(task_id)
            if status == 'SUCCESS':
                result = client.get_task_result(task_id)
        """
        async_result = AsyncResult(task_id, app=self.app)
        status = async_result.status
        logger.debug(f"Task {task_id} status: {status}")
        return status

    def get_task_info(self, task_id: str) -> dict[str, Any]:
        """Get detailed information about a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dictionary with task information including status, result, traceback, etc.
            
        Example:
            info = client.get_task_info(task_id)
            print(f"Status: {info['status']}")
            if info['status'] == 'FAILURE':
                print(f"Error: {info['traceback']}")
        """
        async_result = AsyncResult(task_id, app=self.app)
        info = {
            'id': task_id,
            'status': async_result.status,
            'result': async_result.result,
            'traceback': async_result.traceback,
            'successful': async_result.successful(),
            'failed': async_result.failed(),
            'ready': async_result.ready(),
        }
        logger.debug(f"Task {task_id} info: {info}")
        return info

    def revoke_task(self, task_id: str, terminate: bool = False, signal: str = 'SIGTERM') -> None:
        """Revoke a task.
        
        Args:
            task_id: ID of the task to revoke
            terminate: Whether to terminate the task if it's running
            signal: Signal to send when terminating (default: SIGTERM)
            
        Example:
            client.revoke_task(task_id, terminate=True)
        """
        logger.info(f"Revoking task: {task_id}")
        self.app.control.revoke(task_id, terminate=terminate, signal=signal)

    def purge_queue(self, queue_name: str) -> int:
        """Purge all messages from a queue.
        
        Args:
            queue_name: Name of the queue to purge
            
        Returns:
            Number of messages purged
            
        Example:
            purged_count = client.purge_queue('my_queue')
        """
        logger.warning(f"Purging queue: {queue_name}")
        result = self.app.control.purge()
        # Note: purge() returns a list of responses from workers
        # The actual count depends on the broker implementation
        return len(result) if result else 0

    def get_active_tasks(self) -> dict[str, list[dict[str, Any]]]:
        """Get list of active tasks across all workers.
        
        Returns:
            Dictionary mapping worker names to lists of active tasks
            
        Example:
            active_tasks = client.get_active_tasks()
            for worker, tasks in active_tasks.items():
                print(f"Worker {worker} has {len(tasks)} active tasks")
        """
        logger.debug("Getting active tasks")
        inspect = self.app.control.inspect()
        active = inspect.active()
        return active or {}

    def get_scheduled_tasks(self) -> dict[str, list[dict[str, Any]]]:
        """Get list of scheduled tasks across all workers.
        
        Returns:
            Dictionary mapping worker names to lists of scheduled tasks
            
        Example:
            scheduled_tasks = client.get_scheduled_tasks()
        """
        logger.debug("Getting scheduled tasks")
        inspect = self.app.control.inspect()
        scheduled = inspect.scheduled()
        return scheduled or {}

    def ping_workers(self) -> dict[str, str]:
        """Ping all workers to check their status.
        
        Returns:
            Dictionary mapping worker names to their ping responses
            
        Example:
            workers = client.ping_workers()
            online_workers = [name for name, response in workers.items() if response == 'pong']
        """
        logger.debug("Pinging workers")
        inspect = self.app.control.inspect()
        pong = inspect.ping()
        return pong or {}

    def register_task(self, task_func, name: str | None = None) -> Any:
        """Register a task function with the Celery app.
        
        Args:
            task_func: The function to register as a task
            name: Optional name for the task (defaults to function name)
            
        Returns:
            The registered task
            
        Example:
            @client.register_task
            def my_task(x, y):
                return x + y
                
            # Or with custom name:
            @client.register_task(name='custom.task.name')
            def my_task(x, y):
                return x + y
        """
        if name:
            return self.app.task(name=name)(task_func)
        return self.app.task(task_func)


@lru_cache
def get_celery_client() -> CeleryClient:
    """Get a singleton instance of the Celery client.
    
    Returns:
        CeleryClient instance configured with environment settings
    """
    return CeleryClient()


# Convenience functions for common operations
def send_task(
    task_name: str,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    queue: str | None = None,
    **options: Any
) -> str:
    """Send a task using the singleton Celery client.
    
    Args:
        task_name: Name of the task to execute
        args: Positional arguments for the task
        kwargs: Keyword arguments for the task
        queue: Queue name to send the task to
        **options: Additional Celery send_task options
        
    Returns:
        Task ID for tracking the task result
    """
    client = get_celery_client()
    return client.send_task(task_name, args, kwargs, queue, **options)


def get_task_result(task_id: str, timeout: float | None = None) -> Any:
    """Get the result of a task using the singleton Celery client.
    
    Args:
        task_id: ID of the task
        timeout: Timeout in seconds to wait for the result
        
    Returns:
        The task result
    """
    client = get_celery_client()
    return client.get_task_result(task_id, timeout)


def get_task_status(task_id: str) -> str:
    """Get the status of a task using the singleton Celery client.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task status (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
    """
    client = get_celery_client()
    return client.get_task_status(task_id)
