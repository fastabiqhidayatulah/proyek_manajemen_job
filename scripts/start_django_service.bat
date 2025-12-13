@echo off
REM ========================================================
REM Script untuk menjalankan Django Application
REM Project: Management Job Application
REM Port: 4321
REM ========================================================

REM Set working directory ke lokasi project
cd /d "D:\proyek_management_job"

REM Aktifkan virtual environment
call venv\Scripts\activate.bat

REM Set DJANGO_SETTINGS_MODULE (opsional, sudah ada di manage.py)
set DJANGO_SETTINGS_MODULE=config.settings

REM Set encoding UTF-8 untuk handle Unicode characters di template
set PYTHONIOENCODING=utf-8

REM Set public URL untuk Ngrok tunnel
set DJANGO_PUBLIC_URL=https://one-chimp-hardly.ngrok-free.app

REM Jalankan Django development server di port 4321
REM Gunakan 0.0.0.0 agar bisa diakses dari network
python manage.py runserver 0.0.0.0:4321

REM Jika prefer menggunakan IP spesifik atau localhost saja, ubah menjadi:
REM python manage.py runserver 127.0.0.1:4321
