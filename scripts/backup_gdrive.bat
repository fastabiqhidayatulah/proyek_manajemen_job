@echo off
REM Backup to Google Drive - ZIP Format
REM ====================================

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
set COMPRESSED_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.zip

echo STEP 1: Dumping database...
echo Backup file: %BACKUP_FILE%

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
echo File size: %FileSize% bytes
echo.

echo STEP 2: Compressing to ZIP...
powershell -Command "Compress-Archive -Path '%BACKUP_FILE%' -DestinationPath '%COMPRESSED_FILE%' -Force"

if errorlevel 1 (
    echo WARNING: Compression failed, uploading SQL file instead
    set COMPRESSED_FILE=%BACKUP_FILE%
) else (
    echo SUCCESS: Compressed to ZIP!
    del "%BACKUP_FILE%"
)

for %%A in ("%COMPRESSED_FILE%") do set CompressedSize=%%~zA
echo Backup file size: %CompressedSize% bytes
echo.

echo STEP 3: Uploading to Google Drive...
"%RCLONE_PATH%" copy "%COMPRESSED_FILE%" "gdrive:/proyek_management_backup/" --progress

if errorlevel 1 (
    echo ERROR: Upload failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS - BACKUP COMPLETED!
echo ========================================
echo.
echo Backup file: backup_%DB_NAME%_%TIMESTAMP%.zip
echo Size: %CompressedSize% bytes
echo Uploaded to: gdrive:/proyek_management_backup/
echo.

pause
