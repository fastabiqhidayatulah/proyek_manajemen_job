# Setup Windows Task Scheduler for Automated Backup
# =================================================

$ScriptPath = "D:\proyek_management_job\scripts\backup_automation.ps1"
$TaskName = "Backup_Database_GDrive"
$TaskDescription = "Backup database manajemen_pekerjaan_db ke Google Drive setiap hari jam 02:00"
$ScheduleTime = "02:00"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP AUTOMATIC BACKUP SCHEDULER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify script exists
if (!(Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

# Create task action
$ScriptPathQuoted = "`"$ScriptPath`""
$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -File $ScriptPathQuoted"

# Create task trigger (Daily at 02:00)
$TaskTrigger = New-ScheduledTaskTrigger -Daily -At $ScheduleTime

# Create task settings
$TaskSettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -AllowStartIfOnBatteries:$false

# Remove old task if exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed old scheduled task: $TaskName" -ForegroundColor Yellow
}
catch {}

# Register new task
try {
    Register-ScheduledTask -TaskName $TaskName `
        -Action $TaskAction `
        -Trigger $TaskTrigger `
        -Settings $TaskSettings `
        -Description $TaskDescription `
        -User "SYSTEM" `
        -RunLevel Highest `
        -Force | Out-Null

    Write-Host "✓ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Description: $TaskDescription" -ForegroundColor White
    Write-Host "  Schedule: Daily at $ScheduleTime" -ForegroundColor White
    Write-Host "  Script: $ScriptPath" -ForegroundColor White
    Write-Host "  User: SYSTEM" -ForegroundColor White
    Write-Host ""
    
    # Show task info
    $Task = Get-ScheduledTask -TaskName $TaskName
    Write-Host "Task Information:" -ForegroundColor Cyan
    Write-Host "  Status: $($Task.State)" -ForegroundColor White
    Write-Host "  Last Run: $($Task.LastRunTime)" -ForegroundColor White
    Write-Host "  Last Result: $($Task.LastTaskResult)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Next Steps:" -ForegroundColor Green
    Write-Host "  1. Test manual backup:" -ForegroundColor Gray
    Write-Host "     powershell -ExecutionPolicy Bypass -File `"$ScriptPath`"" -ForegroundColor Gray
    Write-Host "  2. Check log file: D:\proyek_management_job\backups\backup_log.txt" -ForegroundColor Gray
    Write-Host "  3. Verify in Task Scheduler: taskschd.msc" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "ERROR: Failed to create scheduled task: $_" -ForegroundColor Red
    exit 1
}
