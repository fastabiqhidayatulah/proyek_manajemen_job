from django.apps import AppConfig


class MeetingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meetings'
    
    def ready(self):
        """Import signals and tasks when app is ready"""
        import meetings.signals
        try:
            import meetings.tasks
        except ImportError:
            pass  # Celery not installed

