@echo off
REM Simple Backup to Google Drive
REM ==============================

setlocal disabledelayedexpansion

set POSTGRESQL_BIN=C:\Program Files\PostgreSQL\16\bin
set RCLONE_PATH=C:\Program Files\rclone\rclone.exe
set BACKUP_DIR=D:\proyek_management_job\backups
set DB_NAME=manajemen_pekerjaan_db
set DB_USER=manajemen_app_user
set DB_PASSWORD=AppsPassword123!
set DB_HOST=localhost

echo.
echo ========================================
echo BACKUP DATABASE TO GOOGLE DRIVE
echo ========================================
echo.

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%
set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.sql

echo STEP 1: Dumping database...

setlocal enabledelayedexpansion
set PGPASSWORD=%DB_PASSWORD%
"%POSTGRESQL_BIN%\pg_dump" -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "%BACKUP_FILE%"
setlocal disabledelayedexpansion

if errorlevel 1 (
    echo ERROR: Database dump failed!
    pause
    exit /b 1
)

echo SUCCESS: Database dumped!
for %%A in ("%BACKUP_FILE%") do set FileSize=%%~zA
set /A FileSizeMB=%FileSize:~0,-6%
echo File size: %FileSizeMB% MB
echo.

echo STEP 2: Uploading to Google Drive...
echo File: %BACKUP_FILE%
echo.

"%RCLONE_PATH%" copy "%BACKUP_FILE%" "gdrive:/proyek_management_backup/" -v

if errorlevel 1 (
    echo ERROR: Upload failed!
    echo Troubleshooting:
    echo - Check internet connection
    echo - Verify rclone remote: rclone listremotes
    echo - Test connection: rclone lsd gdrive:/
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS - BACKUP COMPLETED!
echo ========================================
echo.
echo Backup file: backup_%DB_NAME%_%TIMESTAMP%.sql
echo Size: %FileSizeMB% MB
echo Uploaded to: gdrive:/proyek_management_backup/
echo Location: %BACKUP_FILE%
echo.

pause
