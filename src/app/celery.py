import os

from celery import Celery
from celery_once import QueueOnce
from django.conf import settings

__all__ = [
    'celery',
    'QueueOnce',
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

celery = Celery('app')

celery.config_from_object(settings)
celery.conf.ONCE = settings.CELERY_ONCE

celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
