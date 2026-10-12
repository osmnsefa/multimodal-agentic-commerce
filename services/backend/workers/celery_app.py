import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    celery_app = Celery(
        "aegis_tasks",
        broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/1",
        backend=settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/2",
        include=["workers.tasks"]
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    celery_app.autodiscover_tasks(["workers"])
except ImportError:
    logger.warning("Celery not installed in environment, falling back to MockCelery.")
    class MockTask:
        def __init__(self, func):
            self.func = func
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        def delay(self, *args, **kwargs):
            class AsyncResult:
                id = "mock-task-id"
            return AsyncResult()

    class MockCelery:
        conf = {}
        def task(self, *args, **kwargs):
            def decorator(f):
                return MockTask(f)
            return decorator
        def autodiscover_tasks(self, *args, **kwargs):
            pass

    celery_app = MockCelery()

@celery_app.task(name="workers.celery_app.ping_task")
def ping_task():
    return "pong"
