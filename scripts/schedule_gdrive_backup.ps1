# Schedule Backup to Google Drive using Windows Task Scheduler
# ============================================================
# Script: schedule_gdrive_backup.ps1
# Usage: powershell -ExecutionPolicy Bypass -File "schedule_gdrive_backup.ps1"

$ScriptPath = "D:\proyek_management_job\scripts\backup_to_gdrive.ps1"
$TaskName = "Proyek_Management_Backup_GDrive"
$TaskDescription = "Backup database proyek_management ke Google Drive setiap hari jam 02:00"
$Time = "02:00"  # Waktu eksekusi: 02:00 pagi
$User = $env:USERNAME

# ================================================
# VALIDATE SCRIPT EXISTS
# ================================================
if (!(Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script tidak ditemukan: $ScriptPath" -ForegroundColor Red
    exit 1
}

# ================================================
# CREATE SCHEDULED TASK
# ================================================
Write-Host "Membuat scheduled task untuk backup otomatis..." -ForegroundColor Green

$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`""

$TaskTrigger = New-ScheduledTaskTrigger -Daily -At $Time

$TaskSettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -AllowStartIfOnBatteries:$false `
    -StopIfGoingOnBatteries:$false

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task lama dihapus: $TaskName" -ForegroundColor Yellow
}
catch {}

# Register new task
try {
    Register-ScheduledTask -TaskName $TaskName `
        -Action $TaskAction `
        -Trigger $TaskTrigger `
        -Settings $TaskSettings `
        -Description $TaskDescription `
        -User "$env:COMPUTERNAME\$User" `
        -RunLevel Highest `
        -Force

    Write-Host "✓ Scheduled task berhasil dibuat!" -ForegroundColor Green
    Write-Host "  Task Name: $TaskName" -ForegroundColor Cyan
    Write-Host "  Waktu eksekusi: $Time setiap hari" -ForegroundColor Cyan
    Write-Host "  Script: $ScriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Untuk melihat task scheduler:" -ForegroundColor Yellow
    Write-Host "  1. Buka 'Task Scheduler' di Windows" -ForegroundColor Gray
    Write-Host "  2. Cari task: $TaskName" -ForegroundColor Gray
    Write-Host "  3. Atau jalankan: taskmgr atau taskschd.msc" -ForegroundColor Gray
}
catch {
    Write-Host "ERROR: Gagal membuat scheduled task: $_" -ForegroundColor Red
    exit 1
}

# ================================================
# DISPLAY TASK INFORMATION
# ================================================
Write-Host ""
Write-Host "Informasi Task yang Dibuat:" -ForegroundColor Cyan
$Task = Get-ScheduledTask -TaskName $TaskName
$Task | Select-Object TaskName, Description, @{N='LastRunTime';E={$_.LastRunTime}}, @{N='NextRunTime';E={$_.NextRunTime}} | Format-Table
