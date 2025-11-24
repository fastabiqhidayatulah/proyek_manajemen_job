@echo off
REM Script untuk setup project Django di server lokal
REM Jalankan sebagai Administrator

setlocal enabledelayedexpansion

echo.
echo ========================================
echo SETUP DJANGO SERVER LOKAL
echo ========================================
echo.

REM Set folder project
set PROJECT_PATH=D:\server_apps\proyek_manajemen_job
set VENV_PATH=%PROJECT_PATH%\venv

if not exist "%PROJECT_PATH%" (
    echo ERROR: Project folder tidak ditemukan di %PROJECT_PATH%
    echo Silakan sesuaikan path di script ini
    pause
    exit /b 1
)

echo [1/6] Masuk folder project...
cd /d "%PROJECT_PATH%" || exit /b 1
echo OK: %CD%
echo.

echo [2/6] Membuat virtual environment...
if not exist "%VENV_PATH%" (
    python -m venv "%VENV_PATH%"
    echo OK: Virtual environment dibuat
) else (
    echo OK: Virtual environment sudah ada
)
echo.

echo [3/6] Activate virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
echo OK: Virtual environment activated
echo.

echo [4/6] Install dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo OK: Dependencies terinstall
echo.

echo [5/6] Migrasi database...
python manage.py migrate
echo OK: Database ter-migrasi
echo.

echo [6/6] Collect static files...
python manage.py collectstatic --noinput
echo OK: Static files dikumpulkan
echo.

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Buat superuser: python manage.py createsuperuser
echo 2. Test server: python manage.py runserver 0.0.0.0:1234
echo 3. Setup auto-start (lihat SETUP_SERVER_LOKAL.md)
echo.
pause
