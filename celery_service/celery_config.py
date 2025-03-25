from celery import Celery


celery = Celery(
    'celery_services',
    broker='redis://localhost:6379/8',
    backend='redis://localhost:6379/8'
)


celery.conf.update(
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

from . import tasks
