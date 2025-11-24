@echo off
REM Script untuk menjalankan Django server di port 1234
REM Simpan di folder project atau di Startup folder untuk auto-start

setlocal enabledelayedexpansion

set PROJECT_PATH=D:\server_apps\proyek_manajemen_job
set VENV_PATH=%PROJECT_PATH%\venv
set PORT=1234

REM Ubah ke project directory
cd /d "%PROJECT_PATH%"

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Run Django server
echo.
echo ========================================
echo STARTING DJANGO SERVER
echo ========================================
echo Project: %PROJECT_PATH%
echo Port: %PORT%
echo Time: %date% %time%
echo ========================================
echo.

python manage.py runserver 0.0.0.0:%PORT%
