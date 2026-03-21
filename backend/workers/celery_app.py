from celery import Celery
from core.config import get_settings

settings = get_settings()

celery = Celery(
    "simworld_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.ingest", "workers.simulation", "workers.report"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
    worker_concurrency=4, # Adjust based on instance size
)
