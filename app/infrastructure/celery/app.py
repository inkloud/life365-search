from celery import Celery  # type: ignore

from app.settings import Settings, get_settings

settings: Settings = get_settings()

celery_app: Celery = Celery(
    "life365_search",
    broker=settings.rabbitmq_url,
    include=["app.infrastructure.celery.tasks"],
)

celery_app.conf.update(  # type: ignore
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
