@echo off
setlocal enabledelayedexpansion
cd /d C:\repos\proyek_manajemen_job
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
set DJANGO_ENVIRONMENT=production
set DJANGO_SETTINGS_MODULE=config.settings
set PYTHONUNBUFFERED=1
celery -A config worker --loglevel=info --concurrency=4 --logfile=C:\logs\management-job\celery_worker.log
if errorlevel 1 (
    echo Celery worker failed to start.
    pause
)
