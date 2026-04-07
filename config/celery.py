"""
Celery configuration untuk Django project.

Dokumentasi: https://docs.celeryproject.io/en/stable/django/
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('manajemen_pekerjaan')

# Load config dari Django settings
# Semua CELERY_* settings akan di-load
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks dari semua registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Task untuk debug/testing"""
    print(f'Request: {self.request!r}')


# Configure Celery Beat Schedule
app.conf.beat_schedule = {
    'send-meeting-reminders-every-5-minutes': {
        'task': 'meetings.tasks.send_meeting_reminders_task',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'default'}
    },
}

# Default queue name
app.conf.task_default_queue = 'default'
