@echo off
REM ========================================================
REM Script untuk uninstall NSSM Service
REM Project: Management Job Application
REM ========================================================

REM CATATAN: Jalankan script ini sebagai Administrator!

echo ========================================================
echo Uninstalling Django Application Service
echo ========================================================
echo.

REM Tentukan lokasi NSSM (sesuaikan dengan lokasi NSSM Anda)
set NSSM_PATH=nssm.exe

REM Nama service
set SERVICE_NAME=DjangoManagementJob

echo Stopping service: %SERVICE_NAME%
net stop %SERVICE_NAME%

echo.
echo Removing service: %SERVICE_NAME%
%NSSM_PATH% remove %SERVICE_NAME% confirm

echo.
echo ========================================================
echo Service uninstalled successfully!
echo ========================================================
echo.

pause
