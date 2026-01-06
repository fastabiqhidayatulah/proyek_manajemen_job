@echo off
REM Test Backup Script - Simple Version
REM ====================================

setlocal disabledelayedexpansion

set POSTGRESQL_BIN=C:\Program Files\PostgreSQL\16\bin
set BACKUP_DIR=D:\proyek_management_job\backups
set DB_NAME=manajemen_pekerjaan_db
set DB_USER=manajemen_app_user
set DB_PASSWORD=AppsPassword123!
set DB_HOST=localhost

echo.
echo ====================================
echo TEST DATABASE BACKUP
echo ====================================
echo.

REM Create backup directory if not exists
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
    echo Created backup directory: %BACKUP_DIR%
)

REM Generate filename
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%
set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.sql

echo Backup file: %BACKUP_FILE%
echo.

REM Dump database
echo Dumping database...
setlocal enabledelayedexpansion
set PGPASSWORD=%DB_PASSWORD%
"%POSTGRESQL_BIN%\pg_dump" -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "%BACKUP_FILE%"
setlocal disabledelayedexpansion

if errorlevel 1 (
    echo ERROR: Database dump failed!
    pause
    exit /b 1
)

echo.
echo SUCCESS! Backup file created.
echo.

REM Show file size
for %%A in ("%BACKUP_FILE%") do (
    set FileSize=%%~zA
)

REM Convert bytes to MB (rough estimate)
set /A FileSizeMB=%FileSize:~0,-6%
echo File size: %FileSizeMB% MB
echo.
echo Backup file location: %BACKUP_FILE%
echo.

pause
