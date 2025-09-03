"""Celery client for asynchronous job processing with RabbitMQ and Redis."""

import logging
from typing import Any
from functools import lru_cache
import time

from celery import Celery
from celery.result import AsyncResult, GroupResult
from celery import group

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

    def send_bulk_tasks(
        self,
        tasks: list[dict[str, Any]],
        queue: str | None = None,
        **options: Any
    ) -> list[str]:
        """Send multiple tasks as a bulk operation.
        
        Args:
            tasks: List of task dictionaries, each containing:
                   - task_name: Name of the task to execute
                   - args: Optional positional arguments for the task
                   - kwargs: Optional keyword arguments for the task
                   - queue: Optional queue name to override default
            queue: Default queue name for all tasks (can be overridden per task)
            **options: Additional Celery options applied to all tasks
            
        Returns:
            List of task IDs for tracking the task results
            
        Example:
            tasks = [
                {
                    'task_name': 'my_app.tasks.process_data',
                    'args': [1, 2, 3],
                    'kwargs': {'option': 'value1'}
                },
                {
                    'task_name': 'my_app.tasks.process_data',
                    'args': [4, 5, 6],
                    'kwargs': {'option': 'value2'},
                    'queue': 'priority_queue'
                }
            ]
            task_ids = client.send_bulk_tasks(tasks)
        """
        logger.info(f"Sending bulk operation with {len(tasks)} tasks")
        
        task_ids = []
        
        for task_config in tasks:
            task_name = task_config.get('task_name')
            if not task_name:
                raise ValueError("Each task must have a 'task_name' field")
            
            task_args = task_config.get('args', ())
            task_kwargs = task_config.get('kwargs', {})
            task_queue = task_config.get('queue', queue)
            
            send_options = {}
            if task_queue:
                send_options['queue'] = task_queue
            send_options.update(options)
            
            task_id = self.send_task(
                task_name,
                args=task_args,
                kwargs=task_kwargs,
                **send_options
            )
            task_ids.append(task_id)
        
        logger.info(f"Bulk operation submitted {len(task_ids)} tasks with IDs: {task_ids}")
        return task_ids

    def send_bulk_tasks_as_group(
        self,
        tasks: list[dict[str, Any]],
        queue: str | None = None,
        **options: Any
    ) -> str:
        """Send multiple tasks as a Celery group for coordinated execution.
        
        Args:
            tasks: List of task dictionaries, each containing:
                   - task_name: Name of the task to execute
                   - args: Optional positional arguments for the task
                   - kwargs: Optional keyword arguments for the task
            queue: Queue name for all tasks in the group
            **options: Additional Celery options applied to all tasks
            
        Returns:
            Group result ID for tracking all tasks in the group
            
        Example:
            tasks = [
                {
                    'task_name': 'my_app.tasks.process_data',
                    'args': [1, 2, 3],
                    'kwargs': {'option': 'value1'}
                },
                {
                    'task_name': 'my_app.tasks.process_data',
                    'args': [4, 5, 6],
                    'kwargs': {'option': 'value2'}
                }
            ]
            group_id = client.send_bulk_tasks_as_group(tasks)
        """
        logger.info(f"Sending group operation with {len(tasks)} tasks")
        
        # Create a list of task signatures
        task_signatures = []
        
        for task_config in tasks:
            task_name = task_config.get('task_name')
            if not task_name:
                raise ValueError("Each task must have a 'task_name' field")
            
            task_args = task_config.get('args', ())
            task_kwargs = task_config.get('kwargs', {})
            
            # Create task signature
            signature = self.app.signature(
                task_name,
                args=task_args,
                kwargs=task_kwargs,
                queue=queue,
                **options
            )
            task_signatures.append(signature)
        
        # Create and apply the group
        job = group(task_signatures)
        result = job.apply_async()
        
        logger.info(f"Group operation submitted with ID: {result.id}")
        return result.id

    def wait_for_all_tasks(
        self,
        task_ids: list[str],
        timeout: float | None = None,
        poll_interval: float = 1.0
    ) -> dict[str, Any]:
        """Wait for all tasks in a list to complete.
        
        Args:
            task_ids: List of task IDs to wait for
            timeout: Total timeout in seconds to wait for all tasks
            poll_interval: How often to check task status (in seconds)
            
        Returns:
            Dictionary with completion status and results:
            {
                'completed': bool,
                'success_count': int,
                'failure_count': int,
                'pending_count': int,
                'results': dict[task_id, result],
                'errors': dict[task_id, error],
                'statuses': dict[task_id, status]
            }
            
        Example:
            task_ids = client.send_bulk_tasks(tasks)
            results = client.wait_for_all_tasks(task_ids, timeout=300)
            if results['completed']:
                print(f"All tasks completed. {results['success_count']} succeeded.")
            else:
                print(f"Timeout reached. {results['pending_count']} tasks still pending.")
        """
        logger.info(f"Waiting for {len(task_ids)} tasks to complete")
        
        start_time = time.time()
        results = {}
        errors = {}
        statuses = {}
        
        while True:
            # Check status of all tasks
            pending_tasks = []
            success_count = 0
            failure_count = 0
            
            for task_id in task_ids:
                if task_id in results or task_id in errors:
                    continue  # Already processed
                
                async_result = AsyncResult(task_id, app=self.app)
                status = async_result.status
                statuses[task_id] = status
                
                if status == 'SUCCESS':
                    try:
                        results[task_id] = async_result.result
                        success_count += 1
                    except Exception as e:
                        errors[task_id] = str(e)
                        failure_count += 1
                elif status in ['FAILURE', 'REVOKED']:
                    try:
                        errors[task_id] = async_result.result or async_result.traceback
                        failure_count += 1
                    except Exception as e:
                        errors[task_id] = str(e)
                        failure_count += 1
                else:
                    pending_tasks.append(task_id)
            
            # Update counters including already processed tasks
            total_success = len(results)
            total_failure = len(errors)
            total_pending = len(pending_tasks)
            
            logger.debug(f"Task status: {total_success} success, {total_failure} failed, {total_pending} pending")
            
            # Check if all tasks are done
            if not pending_tasks:
                logger.info(f"All tasks completed. Success: {total_success}, Failed: {total_failure}")
                return {
                    'completed': True,
                    'success_count': total_success,
                    'failure_count': total_failure,
                    'pending_count': 0,
                    'results': results,
                    'errors': errors,
                    'statuses': statuses
                }
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning(f"Timeout reached after {elapsed:.1f}s. {total_pending} tasks still pending")
                    return {
                        'completed': False,
                        'success_count': total_success,
                        'failure_count': total_failure,
                        'pending_count': total_pending,
                        'results': results,
                        'errors': errors,
                        'statuses': statuses
                    }
            
            # Wait before next poll
            time.sleep(poll_interval)

    def wait_for_group(
        self,
        group_id: str,
        timeout: float | None = None,
        poll_interval: float = 1.0
    ) -> dict[str, Any]:
        """Wait for a Celery group to complete.
        
        Args:
            group_id: ID of the group to wait for
            timeout: Timeout in seconds to wait for the group
            poll_interval: How often to check group status (in seconds)
            
        Returns:
            Dictionary with completion status and results:
            {
                'completed': bool,
                'success_count': int,
                'failure_count': int,
                'pending_count': int,
                'results': list[result],
                'group_result': GroupResult
            }
            
        Example:
            group_id = client.send_bulk_tasks_as_group(tasks)
            results = client.wait_for_group(group_id, timeout=300)
            if results['completed']:
                print(f"Group completed. Results: {results['results']}")
        """
        logger.info(f"Waiting for group {group_id} to complete")
        
        group_result = GroupResult.restore(group_id, app=self.app)
        
        start_time = time.time()
        
        while True:
            if group_result.ready():
                try:
                    results = group_result.get(propagate=False)
                    success_count = sum(1 for r in group_result.results if r.successful())
                    failure_count = sum(1 for r in group_result.results if r.failed())
                    
                    logger.info(f"Group {group_id} completed. Success: {success_count}, Failed: {failure_count}")
                    
                    return {
                        'completed': True,
                        'success_count': success_count,
                        'failure_count': failure_count,
                        'pending_count': 0,
                        'results': results,
                        'group_result': group_result
                    }
                except Exception as e:
                    logger.error(f"Error getting group results: {e}")
                    return {
                        'completed': False,
                        'success_count': 0,
                        'failure_count': len(group_result.results),
                        'pending_count': 0,
                        'results': [],
                        'group_result': group_result,
                        'error': str(e)
                    }
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    completed_count = sum(1 for r in group_result.results if r.ready())
                    pending_count = len(group_result.results) - completed_count
                    
                    logger.warning(f"Group {group_id} timeout after {elapsed:.1f}s. {pending_count} tasks pending")
                    
                    return {
                        'completed': False,
                        'success_count': sum(1 for r in group_result.results if r.successful()),
                        'failure_count': sum(1 for r in group_result.results if r.failed()),
                        'pending_count': pending_count,
                        'results': [],
                        'group_result': group_result
                    }
            
            # Wait before next poll
            time.sleep(poll_interval)


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


def send_bulk_tasks(
    tasks: list[dict[str, Any]],
    queue: str | None = None,
    **options: Any
) -> list[str]:
    """Send multiple tasks as a bulk operation using the singleton Celery client.
    
    Args:
        tasks: List of task dictionaries, each containing:
               - task_name: Name of the task to execute
               - args: Optional positional arguments for the task
               - kwargs: Optional keyword arguments for the task
               - queue: Optional queue name to override default
        queue: Default queue name for all tasks (can be overridden per task)
        **options: Additional Celery options applied to all tasks
        
    Returns:
        List of task IDs for tracking the task results
    """
    client = get_celery_client()
    return client.send_bulk_tasks(tasks, queue, **options)


def send_bulk_tasks_as_group(
    tasks: list[dict[str, Any]],
    queue: str | None = None,
    **options: Any
) -> str:
    """Send multiple tasks as a Celery group using the singleton Celery client.
    
    Args:
        tasks: List of task dictionaries, each containing:
               - task_name: Name of the task to execute
               - args: Optional positional arguments for the task
               - kwargs: Optional keyword arguments for the task
        queue: Queue name for all tasks in the group
        **options: Additional Celery options applied to all tasks
        
    Returns:
        Group result ID for tracking all tasks in the group
    """
    client = get_celery_client()
    return client.send_bulk_tasks_as_group(tasks, queue, **options)


def wait_for_all_tasks(
    task_ids: list[str],
    timeout: float | None = None,
    poll_interval: float = 1.0
) -> dict[str, Any]:
    """Wait for all tasks in a list to complete using the singleton Celery client.
    
    Args:
        task_ids: List of task IDs to wait for
        timeout: Total timeout in seconds to wait for all tasks
        poll_interval: How often to check task status (in seconds)
        
    Returns:
        Dictionary with completion status and results
    """
    client = get_celery_client()
    return client.wait_for_all_tasks(task_ids, timeout, poll_interval)


def wait_for_group(
    group_id: str,
    timeout: float | None = None,
    poll_interval: float = 1.0
) -> dict[str, Any]:
    """Wait for a Celery group to complete using the singleton Celery client.
    
    Args:
        group_id: ID of the group to wait for
        timeout: Timeout in seconds to wait for the group
        poll_interval: How often to check group status (in seconds)
        
    Returns:
        Dictionary with completion status and results
    """
    client = get_celery_client()
    return client.wait_for_group(group_id, timeout, poll_interval)
