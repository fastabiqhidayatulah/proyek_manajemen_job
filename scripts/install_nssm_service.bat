@echo off
REM ========================================================
REM Script untuk install NSSM Service
REM Project: Management Job Application
REM ========================================================

REM CATATAN: Jalankan script ini sebagai Administrator!

echo ========================================================
echo Installing Django Application as Windows Service
echo ========================================================
echo.

REM Tentukan lokasi NSSM - Auto detect dari beberapa lokasi umum
set NSSM_PATH=

REM Cek di folder tools project
if exist "D:\proyek_management_job\tools\nssm.exe" (
    set NSSM_PATH=D:\proyek_management_job\tools\nssm.exe
    echo Found NSSM at: D:\proyek_management_job\tools\nssm.exe
    goto :nssm_found
)

REM Cek di folder scripts
if exist "D:\proyek_management_job\scripts\nssm.exe" (
    set NSSM_PATH=D:\proyek_management_job\scripts\nssm.exe
    echo Found NSSM at: D:\proyek_management_job\scripts\nssm.exe
    goto :nssm_found
)

REM Cek di C:\nssm
if exist "C:\nssm\nssm.exe" (
    set NSSM_PATH=C:\nssm\nssm.exe
    echo Found NSSM at: C:\nssm\nssm.exe
    goto :nssm_found
)

REM Cek di C:\nssm\win64
if exist "C:\nssm\win64\nssm.exe" (
    set NSSM_PATH=C:\nssm\win64\nssm.exe
    echo Found NSSM at: C:\nssm\win64\nssm.exe
    goto :nssm_found
)

REM Cek di PATH (jika sudah diinstall global)
where nssm.exe >nul 2>&1
if %errorlevel% equ 0 (
    set NSSM_PATH=nssm.exe
    echo Found NSSM in system PATH
    goto :nssm_found
)

REM Tidak ditemukan
echo ERROR: nssm.exe tidak ditemukan!
echo.
echo Silakan letakkan nssm.exe di salah satu lokasi berikut:
echo   1. D:\proyek_management_job\tools\nssm.exe  (RECOMMENDED)
echo   2. D:\proyek_management_job\scripts\nssm.exe
echo   3. C:\nssm\nssm.exe
echo   4. Atau tambahkan ke System PATH
echo.
pause
exit /b 1

:nssm_found

REM Nama service
set SERVICE_NAME=DjangoManagementJob

REM Path ke script bat
set BAT_PATH=D:\proyek_management_job\scripts\start_django_service.bat

echo Installing service: %SERVICE_NAME%
echo.

REM Install service menggunakan NSSM
%NSSM_PATH% install %SERVICE_NAME% "%BAT_PATH%"

REM Set description untuk service
%NSSM_PATH% set %SERVICE_NAME% Description "Django Management Job Application - Port 4321"

REM Set startup directory
%NSSM_PATH% set %SERVICE_NAME% AppDirectory "D:\proyek_management_job"

REM Set service untuk auto-start
%NSSM_PATH% set %SERVICE_NAME% Start SERVICE_AUTO_START

REM Set AppStopMethodSkip agar bisa di-stop dengan baik
%NSSM_PATH% set %SERVICE_NAME% AppStopMethodSkip 0

REM Set AppStopMethodConsole untuk graceful shutdown
%NSSM_PATH% set %SERVICE_NAME% AppStopMethodConsole 1500

REM Set log files (opsional)
%NSSM_PATH% set %SERVICE_NAME% AppStdout "D:\proyek_management_job\logs\service_stdout.log"
%NSSM_PATH% set %SERVICE_NAME% AppStderr "D:\proyek_management_job\logs\service_stderr.log"

echo.
echo ========================================================
echo Service installed successfully!
echo.
echo Service Name: %SERVICE_NAME%
echo Port: 4321
echo.
echo Untuk memulai service, jalankan:
echo    net start %SERVICE_NAME%
echo.
echo Atau gunakan Services Manager (services.msc)
echo ========================================================
echo.

pause
