# ============================================================================
# NGROK + DJANGO SETUP SCRIPT - POWERSHELL (Advanced)
# ============================================================================
# Nama file: setup_ngrok.ps1
# Cara pakai: 
#   1. Open PowerShell as Administrator
#   2. cd to project directory\scripts
#   3. Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
#   4. .\setup_ngrok.ps1

param(
    [switch]$AutoStart = $false
)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       NGROK + DJANGO SETUP SCRIPT (PowerShell)             ║" -ForegroundColor Cyan
Write-Host "║    Fitur WhatsApp Checklist Sharing Setup                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# CHECK NGROK
# ============================================================================
Write-Host "🔍 Checking Ngrok installation..." -ForegroundColor Yellow

$ngrokPath = (Get-Command ngrok -ErrorAction SilentlyContinue).Source
if ($null -eq $ngrokPath) {
    Write-Host "❌ ERROR: Ngrok tidak ditemukan!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solusi:" -ForegroundColor Yellow
    Write-Host "1. Download dari: https://ngrok.com/download" -ForegroundColor Gray
    Write-Host "2. Extract ke: C:\Program Files\ngrok" -ForegroundColor Gray
    Write-Host "3. Atau pakai: choco install ngrok" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Ngrok found: $ngrokPath" -ForegroundColor Green
Write-Host ""

# ============================================================================
# START NGROK
# ============================================================================
Write-Host "▶️  Starting Ngrok (port 4321)..." -ForegroundColor Yellow
Write-Host ""

# Start Ngrok in background
$ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "http 4321" -NoNewWindow -PassThru

Write-Host "⏳ Waiting untuk Ngrok startup (5 detik)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# ============================================================================
# GET NGROK URL (dari API)
# ============================================================================
Write-Host ""
Write-Host "📡 Attempting to get Ngrok public URL dari API..." -ForegroundColor Yellow

$maxRetries = 10
$retry = 0
$ngrokUrl = $null

while ($retry -lt $maxRetries -and $null -eq $ngrokUrl) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:4040/api/tunnels" -UseBasicParsing
        $tunnels = $response.Content | ConvertFrom-Json
        
        # Get HTTPS tunnel
        $httpsTunnel = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
        if ($null -ne $httpsTunnel) {
            $ngrokUrl = $httpsTunnel.public_url
            break
        }
    }
    catch {
        # Masih belum ready, tunggu
        $retry++
        if ($retry -lt $maxRetries) {
            Start-Sleep -Seconds 1
        }
    }
}

# Jika API fail, tanya manual
if ($null -eq $ngrokUrl) {
    Write-Host "⚠️  Tidak bisa auto-detect URL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  MANUAL SETUP                                              ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Lihat Ngrok terminal window" -ForegroundColor Gray
    Write-Host "2. Cari baris: 'Forwarding    https://...' " -ForegroundColor Gray
    Write-Host "3. Copy URL (contoh: https://xxxx-xxxx.ngrok.io)" -ForegroundColor Gray
    Write-Host ""
    $ngrokUrl = Read-Host "Paste Ngrok URL"
}
else {
    Write-Host "✅ URL obtained from API!" -ForegroundColor Green
}

# Validate URL
if ([string]::IsNullOrWhiteSpace($ngrokUrl)) {
    Write-Host "❌ ERROR: URL tidak valid!" -ForegroundColor Red
    Stop-Process -InputObject $ngrokProcess -Force -ErrorAction SilentlyContinue
    pause
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Ngrok URL: $ngrokUrl" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# SET ENVIRONMENT VARIABLE
# ============================================================================
Write-Host "🔧 Setting DJANGO_PUBLIC_URL environment variable..." -ForegroundColor Yellow

$env:DJANGO_PUBLIC_URL = $ngrokUrl
[Environment]::SetEnvironmentVariable("DJANGO_PUBLIC_URL", $ngrokUrl, "User")

Write-Host "✅ Environment variable set!" -ForegroundColor Green
Write-Host ""

# Verify
Write-Host "📋 Verification:" -ForegroundColor Yellow
Write-Host "   DJANGO_PUBLIC_URL = $($env:DJANGO_PUBLIC_URL)" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# DJANGO SETUP
# ============================================================================
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NEXT STEPS                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣  Start Django Server" -ForegroundColor Yellow
Write-Host "   cd to project directory" -ForegroundColor Gray
Write-Host "   python manage.py runserver 0.0.0.0:4321" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣  Test URL" -ForegroundColor Yellow
Write-Host "   Buka browser: $ngrokUrl" -ForegroundColor Gray
Write-Host ""

Write-Host "3️⃣  Test Share Checklist" -ForegroundColor Yellow
Write-Host "   Buka: $ngrokUrl/preventive/execution/1/detail/" -ForegroundColor Gray
Write-Host "   Klik 'KIRIM CHECKLIST VIA WHATSAPP'" -ForegroundColor Gray
Write-Host "   Preview URL harus: $ngrokUrl/preventive/checklist-fill/..." -ForegroundColor Gray
Write-Host ""

Write-Host "4️⃣  Send to WhatsApp" -ForegroundColor Yellow
Write-Host "   Pilih penerima → Klik 'KIRIM VIA FONTTE API'" -ForegroundColor Gray
Write-Host "   Link di pesan WA harus: $ngrokUrl/..." -ForegroundColor Gray
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Setup selesai! Ngrok running..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  PENTING:" -ForegroundColor Yellow
Write-Host "   - Jangan tutup Ngrok window" -ForegroundColor Gray
Write-Host "   - Setiap restart Ngrok → update DJANGO_PUBLIC_URL" -ForegroundColor Gray
Write-Host "   - Restart Django setelah set environment variable" -ForegroundColor Gray
Write-Host ""

Write-Host "Ngrok Dashboard: https://dashboard.ngrok.com" -ForegroundColor Cyan
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
