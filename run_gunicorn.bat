@echo off
setlocal enabledelayedexpansion
cd /d C:\repos\proyek_manajemen_job
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
set DJANGO_ENVIRONMENT=production
set DJANGO_SETTINGS_MODULE=config.settings
set PYTHONUNBUFFERED=1
gunicorn config.wsgi:application --workers 4 --bind 127.0.0.1:8001 --timeout 60 --access-logfile C:\logs\management-job\gunicorn_access.log --error-logfile C:\logs\management-job\gunicorn_error.log
if errorlevel 1 (
    echo Gunicorn failed to start.
    pause
)
