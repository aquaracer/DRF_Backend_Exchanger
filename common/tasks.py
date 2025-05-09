from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.conf import settings
import time
from typing import Any, Optional, Dict, List, Tuple

logger = get_task_logger(__name__)


class BaseTask:
    """
    Base task class that provides common functionality for all Celery tasks.
    """
    def __init__(self) -> None:
        self.logger = logger

    def get_lock_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Generate a unique lock key for the task.
        """
        return f"{self.__class__.__name__}:{args}:{kwargs}"

    def acquire_lock(self, lock_key: str, timeout: int = 60) -> bool:
        """
        Try to acquire a lock for the task.
        """
        return cache.add(lock_key, True, timeout)

    def release_lock(self, lock_key: str) -> None:
        """
        Release the lock for the task.
        """
        cache.delete(lock_key)

    def execute_with_lock(self, *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        Execute the task with a lock to prevent concurrent execution.
        """
        lock_key = self.get_lock_key(*args, **kwargs)
        if not self.acquire_lock(lock_key):
            self.logger.warning(f"Task {self.__class__.__name__} is already running")
            return

        try:
            return self.run(*args, **kwargs)
        finally:
            self.release_lock(lock_key)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Main task logic to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement run()")


@shared_task(bind=True, max_retries=3)
def retry_task(self, task_func, *args, **kwargs):
    """
    Task wrapper that provides retry functionality.
    """
    try:
        return task_func(*args, **kwargs)
    except Exception as exc:
        self.logger.error(f"Task {task_func.__name__} failed: {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task
def cleanup_old_data():
    """
    Clean up old data from the database.
    """
    from django.utils import timezone
    from datetime import timedelta

    # Example: Clean up old sessions
    from django.contrib.sessions.models import Session
    Session.objects.filter(expire_date__lt=timezone.now()).delete()

    # Example: Clean up old cache keys
    cache.delete_pattern('*:old_data:*')


@shared_task
def health_check():
    """
    Perform health check of the system.
    """
    from django.db import connection
    from django.db.utils import OperationalError

    try:
        # Check database connection
        connection.cursor()
        db_status = "healthy"
    except OperationalError:
        db_status = "unhealthy"

    try:
        # Check Redis connection
        cache.set('health_check', 'ok', 1)
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    return {
        'timestamp': time.time(),
        'database': db_status,
        'redis': redis_status,
    } 