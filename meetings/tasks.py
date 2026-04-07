"""
Celery tasks untuk meetings app.

Dokumentasi: https://docs.celeryproject.io/
"""

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_meeting_reminders_task(self):
    """
    Celery task untuk mengirim meeting reminders.
    
    Dijalankan setiap 5 menit oleh Celery Beat.
    
    Retry: Up to 3 times with exponential backoff
    """
    try:
        logger.info('[Celery Task] Starting send_meeting_reminders_task...')
        
        # Call management command
        call_command('send_meeting_reminders', '--verbose')
        
        logger.info('[Celery Task] send_meeting_reminders_task completed successfully')
        return {
            'status': 'success',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.exception(f'[Celery Task] Error in send_meeting_reminders_task: {str(exc)}')
        
        # Retry dengan exponential backoff
        # Retry setelah 60 * 2^(retry_count) seconds
        raise self.retry(exc=exc, countdown=60)


@shared_task
def debug_task():
    """Debug task untuk testing Celery"""
    logger.info('[Celery Task] Debug task executed')
    return {
        'status': 'debug_ok',
        'timestamp': timezone.now().isoformat()
    }
