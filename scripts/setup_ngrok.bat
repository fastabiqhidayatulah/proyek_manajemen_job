@echo off
REM ============================================================================
REM NGROK + DJANGO SETUP SCRIPT - WINDOWS BATCH
REM Untuk memudahkan setup Ngrok + set DJANGO_PUBLIC_URL
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          NGROK + DJANGO SETUP SCRIPT                       ║
echo ║   Fitur WhatsApp Checklist Sharing                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Ngrok tidak ditemukan!
    echo.
    echo Silakan:
    echo 1. Download dari https://ngrok.com/download
    echo 2. Extract ke C:\Program Files\ngrok
    echo 3. Atau jalankan: choco install ngrok
    echo.
    pause
    exit /b 1
)

echo ✅ Ngrok ditemukan!
echo.

REM Start Ngrok
echo ▶️  Starting Ngrok (http://localhost:4321)...
echo.
start cmd /k "ngrok http 4321"

echo.
echo ⏳ Waiting 3 seconds untuk Ngrok startup...
timeout /t 3 /nobreak

REM Extract URL dari Ngrok API
echo.
echo 📡 Getting Ngrok public URL...

REM Ngrok API endpoint
set NGROK_API=http://127.0.0.1:4040/api/tunnels

REM Coba get URL (memerlukan curl atau Invoke-WebRequest dari PowerShell)
REM Untuk simplicity, kita gunakan cara manual:

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  MANUAL SETUP - Silakan Copy URL dari Ngrok                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. Lihat terminal Ngrok yang baru terbuka
echo 2. Cari baris: "Forwarding" yang dimulai dengan "https://"
echo 3. Copy URL tersebut (contoh: https://xxxx-xxxx.ngrok.io)
echo.

set /p NGROK_URL="Paste Ngrok URL di sini: "

if "%NGROK_URL%"=="" (
    echo ❌ ERROR: URL tidak boleh kosong!
    pause
    exit /b 1
)

echo.
echo ✅ URL: %NGROK_URL%
echo.

REM Set environment variable
echo 🔧 Setting DJANGO_PUBLIC_URL environment variable...
setx DJANGO_PUBLIC_URL "%NGROK_URL%"

echo ✅ Environment variable set!
echo.

REM Inform user to restart Django
echo ╔════════════════════════════════════════════════════════════╗
echo ║  NEXT STEPS                                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. Buka Terminal Baru (untuk Django)
echo    cd to project directory
echo.
echo 2. Jalankan Django:
echo    python manage.py runserver 0.0.0.0:4321
echo.
echo 3. Test akses:
echo    Buka: %NGROK_URL%
echo.
echo 4. Test share checklist:
echo    Buka execution detail → Klik share button
echo    URL preview harus: %NGROK_URL%/preventive/checklist-fill/...
echo.
echo.
echo ✅ Setup selesai!
echo.

pause
