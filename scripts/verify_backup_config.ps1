# Verify Backup Configuration
# ===========================
# Script: verify_backup_config.ps1
# Usage: powershell -ExecutionPolicy Bypass -File "verify_backup_config.ps1"

$RclonePath = "C:\Program Files\rclone\rclone.exe"
$ProjectPath = "D:\proyek_management_job"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFIKASI KONFIGURASI BACKUP GDRIVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check PostgreSQL pg_dump
Write-Host "1. Checking PostgreSQL pg_dump..." -ForegroundColor Yellow
$pgdump_check = $null
try {
    $pgdump_check = pg_dump --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ pg_dump tersedia: $pgdump_check" -ForegroundColor Green
    } else {
        Write-Host "   ✗ pg_dump NOT FOUND!" -ForegroundColor Red
        Write-Host "   Solusi: Tambahkan PostgreSQL bin ke PATH atau install PostgreSQL Client" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ✗ pg_dump NOT FOUND!" -ForegroundColor Red
    Write-Host "   Solusi: Tambahkan PostgreSQL bin ke PATH atau install PostgreSQL Client" -ForegroundColor Yellow
}

# 2. Check rclone installed
Write-Host ""
Write-Host "2. Checking rclone installation..." -ForegroundColor Yellow
if (Test-Path $RclonePath) {
    $rclone_version = & $RclonePath version
    Write-Host "   ✓ rclone ditemukan: $($rclone_version.Split([Environment]::NewLine)[0])" -ForegroundColor Green
}
else {
    Write-Host "   ✗ rclone NOT FOUND at: $RclonePath" -ForegroundColor Red
    Write-Host "   Silakan install rclone atau ubah path di backup_to_gdrive.ps1" -ForegroundColor Yellow
    exit 1
}

# 3. Check rclone remote configuration
Write-Host ""
Write-Host "3. Checking rclone remote configuration..." -ForegroundColor Yellow
try {
    $remotes = & $RclonePath listremotes
    if ($remotes -contains "gdrive:") {
        Write-Host "   ✓ Remote 'gdrive' tersedia" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ Remote 'gdrive' NOT FOUND!" -ForegroundColor Red
        Write-Host "   Tersedia remote:" -ForegroundColor Yellow
        $remotes | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
        Write-Host "   Solusi: Jalankan 'rclone config' untuk membuat/edit remote" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "   ✗ Error checking remotes: $_" -ForegroundColor Red
    exit 1
}

# 4. Test rclone connection to Google Drive
Write-Host ""
Write-Host "4. Testing connection to Google Drive..." -ForegroundColor Yellow
try {
    $test = & $RclonePath lsd gdrive:/ 2>&1
    Write-Host "   ✓ Connection successful! Folders di gdrive:" -ForegroundColor Green
    if ($test) {
        $test | Select-Object -First 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        if (@($test).Count -gt 5) {
            Write-Host "      ... (dan $(@($test).Count - 5) folder lainnya)" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "   ✗ Connection failed: $_" -ForegroundColor Red
    Write-Host "   Solusi: Verifikasi konfigurasi rclone dan internet connection" -ForegroundColor Yellow
}

# 5. Check backup folder in Google Drive
Write-Host ""
Write-Host "5. Checking backup folder in Google Drive..." -ForegroundColor Yellow
try {
    $backupFolder = & $RclonePath ls gdrive:/proyek_management_backup 2>&1
    if ($backupFolder -and $backupFolder -ne "") {
        $fileCount = @($backupFolder).Count
        Write-Host "   ✓ Folder 'proyek_management_backup' ditemukan dengan $fileCount file(s):" -ForegroundColor Green
        $backupFolder | Select-Object -First 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        if ($fileCount -gt 5) {
            Write-Host "      ... (dan $($fileCount - 5) file lainnya)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ⚠ Folder 'proyek_management_backup' kosong atau belum ada" -ForegroundColor Yellow
        Write-Host "   Folder akan dibuat otomatis pada backup pertama kali" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ⚠ Folder 'proyek_management_backup' belum ada" -ForegroundColor Yellow
    Write-Host "   Akan dibuat otomatis pada backup pertama kali" -ForegroundColor Gray
}

# 6. Check local backup directory
Write-Host ""
Write-Host "6. Checking local backup directory..." -ForegroundColor Yellow
$BackupDir = "$ProjectPath\backups"
if (Test-Path $BackupDir) {
    $backups = Get-ChildItem $BackupDir -Filter "backup_*.gz" | Measure-Object
    Write-Host "   ✓ Directory tersedia: $BackupDir" -ForegroundColor Green
    Write-Host "   Jumlah backup lama: $($backups.Count) file(s)" -ForegroundColor Gray
}
else {
    Write-Host "   ℹ Directory belum ada: $BackupDir" -ForegroundColor Cyan
    Write-Host "   Akan dibuat otomatis pada backup pertama kali" -ForegroundColor Gray
}

# 7. Check backup scripts
Write-Host ""
Write-Host "7. Checking backup scripts..." -ForegroundColor Yellow
$scripts = @(
    "$ProjectPath\scripts\backup_to_gdrive.ps1",
    "$ProjectPath\scripts\schedule_gdrive_backup.ps1"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "   ✓ $(Split-Path $script -Leaf)" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $(Split-Path $script -Leaf) NOT FOUND" -ForegroundColor Red
    }
}

# 8. Check scheduled task
Write-Host ""
Write-Host "8. Checking scheduled task..." -ForegroundColor Yellow
try {
    $task = Get-ScheduledTask -TaskName "Proyek_Management_Backup_GDrive" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "   ✓ Scheduled task ditemukan: Proyek_Management_Backup_GDrive" -ForegroundColor Green
        Write-Host "   Status: $($task.State)" -ForegroundColor Gray
        if ($task.Triggers.Count -gt 0) {
            $trigger = $task.Triggers[0]
            Write-Host "   Jadwal: Setiap hari pada $(if ($trigger.StartBoundary) { $trigger.StartBoundary } else { 'Custom' })" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ℹ Scheduled task belum dibuat" -ForegroundColor Cyan
        Write-Host "   Jalankan schedule_gdrive_backup.ps1 untuk membuat task" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ℹ Scheduled task belum dibuat" -ForegroundColor Cyan
}

# 9. Database connectivity check
Write-Host ""
Write-Host "9. Checking database connectivity..." -ForegroundColor Yellow
$dbtest_check = $null
try {
    $dbtest_check = psql -U postgres -h localhost -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ PostgreSQL database accessible" -ForegroundColor Green
    } else {
        Write-Host "   ✗ PostgreSQL database NOT accessible" -ForegroundColor Red
        Write-Host "   Pastikan PostgreSQL service running dan psql di PATH" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ✗ PostgreSQL database NOT accessible: $_" -ForegroundColor Red
    Write-Host "   Pastikan PostgreSQL service running dan psql di PATH" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Untuk melanjutkan setup backup:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Test manual backup:" -ForegroundColor Green
Write-Host "     powershell -ExecutionPolicy Bypass -File D:\proyek_management_job\scripts\backup_to_gdrive.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Setup automatic scheduling:" -ForegroundColor Green
Write-Host "     powershell -ExecutionPolicy Bypass -File D:\proyek_management_job\scripts\schedule_gdrive_backup.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Baca panduan lengkap:" -ForegroundColor Green
Write-Host "     D:\proyek_management_job\panduan\GDRIVE_BACKUP_SETUP.md" -ForegroundColor Gray
Write-Host ""
