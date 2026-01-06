@echo off
REM Setup Automatic Backup Scheduler
REM ================================

setlocal

set SCRIPT_PATH=D:\proyek_management_job\scripts\backup_automation.ps1
set TASK_NAME=Backup_Database_GDrive
set SCHEDULE_TIME=02:00

echo.
echo ========================================
echo SETUP AUTOMATIC BACKUP SCHEDULER
echo ========================================
echo.

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Script not found: %SCRIPT_PATH%
    pause
    exit /b 1
)

echo Creating scheduled task...
echo Task Name: %TASK_NAME%
echo Schedule: Daily at %SCHEDULE_TIME%
echo Script: %SCRIPT_PATH%
echo.

REM Delete old task if exists
schtasks /delete /tn "%TASK_NAME%" /f 2>nul

REM Create new task
schtasks /create /tn "%TASK_NAME%" ^
    /tr "powershell.exe -ExecutionPolicy Bypass -NoProfile -File \"%SCRIPT_PATH%\"" ^
    /sc daily /st %SCHEDULE_TIME% ^
    /ru SYSTEM /rl HIGHEST /f

if errorlevel 1 (
    echo ERROR: Failed to create scheduled task!
    echo Make sure to run this as Administrator.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Scheduled task created!
echo.

REM Show task info
schtasks /query /tn "%TASK_NAME%" /v /fo list

echo.
echo ========================================
echo SCHEDULER SETUP COMPLETED
echo ========================================
echo.
echo Backup will run daily at %SCHEDULE_TIME%
echo Log file: D:\proyek_management_job\backups\backup_log.txt
echo.
echo To verify in GUI:
echo 1. Open Task Scheduler: taskschd.msc
echo 2. Search for: %TASK_NAME%
echo.

pause
