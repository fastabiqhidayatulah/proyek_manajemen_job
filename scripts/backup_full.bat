@echo off
REM Complete Backup Script - Database to Google Drive
REM ==================================================

setlocal disabledelayedexpansion

set POSTGRESQL_BIN=C:\Program Files\PostgreSQL\16\bin
set RCLONE_PATH=C:\Program Files\rclone\rclone.exe
set BACKUP_DIR=D:\proyek_management_job\backups
set DB_NAME=manajemen_pekerjaan_db
set DB_USER=manajemen_app_user
set DB_PASSWORD=AppsPassword123!
set DB_HOST=localhost

echo.
echo ====================================
echo BACKUP DATABASE TO GOOGLE DRIVE
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
set COMPRESSED_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.zip

echo.
echo STEP 1: Dumping database...
echo Backup file: %BACKUP_FILE%
echo.

REM Dump database
setlocal enabledelayedexpansion
set PGPASSWORD=%DB_PASSWORD%
"%POSTGRESQL_BIN%\pg_dump" -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "%BACKUP_FILE%"
setlocal disabledelayedexpansion

if errorlevel 1 (
    echo ERROR: Database dump failed!
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Database dumped!
echo.

REM Check file size
for %%A in ("%BACKUP_FILE%") do (
    set FileSize=%%~zA
)
echo File size: %FileSize% bytes
echo.

REM Step 2: Compress
echo STEP 2: Compressing backup...
powershell -Command "Compress-Archive -Path '%BACKUP_FILE%' -DestinationPath '%COMPRESSED_FILE%' -Force -ErrorAction Stop" 2>&1

if errorlevel 1 (
    echo ERROR: Compression failed!
    pause
    exit /b 1
)

echo SUCCESS: Compressed!
echo.

REM Delete original SQL file
del "%BACKUP_FILE%"
echo Deleted original SQL file
echo.

REM Check compressed file size
for %%A in ("%COMPRESSED_FILE%") do (
    set CompressedSize=%%~zA
)
echo Compressed file size: %CompressedSize% bytes
echo.

REM Step 3: Upload to Google Drive
echo STEP 3: Uploading to Google Drive...
echo Remote path: gdrive:/proyek_management_backup/
echo.

"%RCLONE_PATH%" copy "%COMPRESSED_FILE%" "gdrive:/proyek_management_backup/" 2>&1

if errorlevel 1 (
    echo ERROR: Upload to Google Drive failed!
    pause
    exit /b 1
)

echo SUCCESS: Uploaded to Google Drive!
echo.

echo ====================================
echo BACKUP COMPLETED SUCCESSFULLY!
echo ====================================
echo.
echo Summary:
echo   Database: %DB_NAME%
echo   Backup file: backup_%DB_NAME%_%TIMESTAMP%.sql.gz
echo   Location: D:\proyek_management_job\backups\
echo   Uploaded to: gdrive:/proyek_management_backup/
echo.
echo Next step: Setup automatic scheduling with schedule_gdrive_backup.ps1
echo.

pause
