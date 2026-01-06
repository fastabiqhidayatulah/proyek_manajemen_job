@echo off
REM Backup Script with Password
REM ============================

setlocal enabledelayedexpansion

set PROJECT_PATH=D:\proyek_management_job
set BACKUP_DIR=%PROJECT_PATH%\backups
set POSTGRESQL_BIN=C:\Program Files\PostgreSQL\16\bin
set RCLONE_PATH=C:\Program Files\rclone\rclone.exe
set DB_NAME=manajemen_pekerjaan_db
set DB_USER=manajemen_app_user
set DB_HOST=localhost
set DB_PORT=5432
set DB_PASSWORD=AppsPassword123!

REM Add PostgreSQL to PATH
set PATH=%PATH%;%POSTGRESQL_BIN%

echo.
echo ========================================
echo BACKUP DATABASE TO GOOGLE DRIVE
echo ========================================
echo.

REM Prompt for password
set /p DB_PASSWORD="Enter PostgreSQL password for '%DB_USER%': "

REM Create backup directory
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
    echo Backup directory created: %BACKUP_DIR%
)

REM Generate filename with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%
set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.sql
set COMPRESSED_FILE=%BACKUP_FILE%.gz

echo Backup file: %BACKUP_FILE%
echo.

REM Step 1: Dump database
echo Step 1: Dumping database...
echo Command: pg_dump -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "%BACKUP_FILE%"
echo.

set PGPASSWORD=%DB_PASSWORD%
pg_dump -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "%BACKUP_FILE%" 2>&1

if errorlevel 1 (
    echo ERROR: Database dump failed!
    echo.
    echo Possible solutions:
    echo 1. Check if PostgreSQL service is running (services.msc)
    echo 2. Verify database password
    echo 3. Check if database exists: psql -U postgres -l
    echo.
    pause
    exit /b 1
)

REM Check file size
for %%A in ("%BACKUP_FILE%") do (
    set FileSize=%%~zA
)
set FileSizeMB=!FileSize:~0,-6!
echo Backup successful! File size: %FileSizeMB% MB
echo.

REM Step 2: Compress using 7-zip or built-in
echo Step 2: Compressing backup...
REM Using PowerShell for compression
powershell -Command "Compress-Archive -Path '%BACKUP_FILE%' -DestinationPath '%COMPRESSED_FILE%' -Force"

if errorlevel 1 (
    echo ERROR: Compression failed!
    exit /b 1
)

REM Delete original file
del "%BACKUP_FILE%"

for %%A in ("%COMPRESSED_FILE%") do (
    set CompressedSize=%%~zA
)
set CompressedSizeMB=!CompressedSize:~0,-6!
echo Compressed successfully! Size: %CompressedSizeMB% MB
echo.

REM Step 3: Upload to Google Drive
echo Step 3: Uploading to Google Drive...
echo Command: rclone copy "%COMPRESSED_FILE%" "gdrive:/proyek_management_backup/"
echo.

"%RCLONE_PATH%" copy "%COMPRESSED_FILE%" "gdrive:/proyek_management_backup/"

if errorlevel 1 (
    echo ERROR: Upload failed!
    pause
    exit /b 1
)

echo Upload completed successfully!
echo.

echo ========================================
echo BACKUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Summary:
echo   Database: %DB_NAME%
echo   Backup file: backup_%DB_NAME%_%TIMESTAMP%.sql.gz
echo   Location: gdrive:/proyek_management_backup/
echo.
pause
