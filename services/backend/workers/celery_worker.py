from workers.celery_app import celery_app, ping_task

__all__ = ["celery_app", "ping_task"]
