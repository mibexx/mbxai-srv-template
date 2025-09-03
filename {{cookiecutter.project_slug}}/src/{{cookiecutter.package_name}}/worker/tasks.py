"""Celery tasks for {{cookiecutter.package_name}}."""

import logging
from typing import Any

from ..utils import get_celery_client


logger = logging.getLogger(__name__)

# Get the Celery app instance
celery_app = get_celery_client().app


@celery_app.task(bind=True)
def example_task(self, data: dict[str, Any]) -> dict[str, Any]:
    """Example Celery task.
    
    Args:
        self: Task instance (bound)
        data: Input data to process
        
    Returns:
        Processed result
        
    Example:
        from {{cookiecutter.package_name}}.utils import send_task
        
        task_id = send_task(
            '{{cookiecutter.package_name}}.worker.tasks.example_task',
            kwargs={'data': {'key': 'value'}}
        )
    """
    logger.info(f"Processing example task with data: {data}")
    
    try:
        # Your task logic here
        result = {
            "status": "success",
            "input_data": data,
            "processed_at": self.request.id,
            "message": "Task completed successfully"
        }
        
        logger.info(f"Task {self.request.id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}")
        # Optionally retry the task
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task
def long_running_task(duration: int = 10) -> str:
    """Example long-running task.
    
    Args:
        duration: How long to run (in seconds)
        
    Returns:
        Completion message
        
    Example:
        from {{cookiecutter.package_name}}.utils import send_task
        
        task_id = send_task(
            '{{cookiecutter.package_name}}.worker.tasks.long_running_task',
            kwargs={'duration': 30}
        )
    """
    import time
    
    logger.info(f"Starting long-running task for {duration} seconds")
    
    # Simulate work
    for i in range(duration):
        time.sleep(1)
        if i % 5 == 0:
            logger.info(f"Progress: {i}/{duration} seconds")
    
    result = f"Long-running task completed after {duration} seconds"
    logger.info(result)
    return result


@celery_app.task
def ai_processing_task(prompt: str, model: str = "gpt-4o-mini") -> dict[str, Any]:
    """Example AI processing task using the MCP client.
    
    Args:
        prompt: The prompt to process
        model: AI model to use
        
    Returns:
        AI response data
        
    Example:
        from {{cookiecutter.package_name}}.utils import send_task
        
        task_id = send_task(
            '{{cookiecutter.package_name}}.worker.tasks.ai_processing_task',
            kwargs={'prompt': 'What is the meaning of life?'}
        )
    """
    from ..utils import get_mcp_client
    
    logger.info(f"Processing AI task with prompt: {prompt[:50]}...")
    
    try:
        client = get_mcp_client()
        
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = {
            "status": "success",
            "prompt": prompt,
            "response": response.get("content", ""),
            "model": model,
            "usage": response.get("usage", {})
        }
        
        logger.info("AI processing task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"AI processing task failed: {str(e)}")
        return {
            "status": "error",
            "prompt": prompt,
            "error": str(e),
            "model": model
        }
