# Simple Backup Test Script
# ========================
# Cek konfigurasi backup tanpa try-catch yang kompleks

$RclonePath = "C:\Program Files\rclone\rclone.exe"
$ProjectPath = "D:\proyek_management_job"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP CONFIGURATION TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check rclone
Write-Host "1. Checking rclone..." -ForegroundColor Yellow
if (Test-Path $RclonePath) {
    Write-Host "   ✓ rclone found at: $RclonePath" -ForegroundColor Green
    & $RclonePath --version
} else {
    Write-Host "   ✗ rclone NOT found at: $RclonePath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. List rclone remotes
Write-Host "2. Checking rclone remotes..." -ForegroundColor Yellow
$remotes = & $RclonePath listremotes
Write-Host "   Available remotes:" -ForegroundColor Green
$remotes | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }

if ($remotes -contains "gdrive:") {
    Write-Host "   ✓ 'gdrive' remote is configured" -ForegroundColor Green
} else {
    Write-Host "   ✗ 'gdrive' remote NOT found!" -ForegroundColor Red
    Write-Host "   Please run: rclone config" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 3. Test connection to Google Drive
Write-Host "3. Testing Google Drive connection..." -ForegroundColor Yellow
$folders = & $RclonePath lsd gdrive:/ 2>&1
if ($folders) {
    Write-Host "   ✓ Connection successful!" -ForegroundColor Green
    Write-Host "   Folders in Google Drive:" -ForegroundColor Gray
    $folders | Select-Object -First 10 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
} else {
    Write-Host "   ✗ Connection failed!" -ForegroundColor Red
}

Write-Host ""

# 4. Check backup folder in Google Drive
Write-Host "4. Checking backup folder..." -ForegroundColor Yellow
$backupFolder = & $RclonePath ls gdrive:/proyek_management_backup 2>&1
if ($backupFolder) {
    $fileCount = @($backupFolder | Measure-Object).Count
    Write-Host "   ✓ Folder 'proyek_management_backup' exists with $fileCount files:" -ForegroundColor Green
    $backupFolder | Select-Object -First 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
    if ($fileCount -gt 5) {
        Write-Host "      ... (+$($fileCount - 5) more)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ℹ Folder 'proyek_management_backup' not found (will be created on first backup)" -ForegroundColor Cyan
}

Write-Host ""

# 5. Check local backup directory
Write-Host "5. Checking local backup directory..." -ForegroundColor Yellow
$BackupDir = "$ProjectPath\backups"
if (Test-Path $BackupDir) {
    $backups = @(Get-ChildItem $BackupDir -Filter "backup_*.gz" -ErrorAction SilentlyContinue)
    Write-Host "   ✓ Directory exists: $BackupDir" -ForegroundColor Green
    if ($backups.Count -gt 0) {
        Write-Host "   Found $($backups.Count) backup file(s):" -ForegroundColor Gray
        $backups | Select-Object -Last 3 | ForEach-Object { 
            $size = [math]::Round($_.Length / 1MB, 2)
            Write-Host "      $($_.Name) ($size MB)" -ForegroundColor Gray 
        }
    } else {
        Write-Host "   No backup files yet" -ForegroundColor Gray
    }
} else {
    Write-Host "   ℹ Directory not created yet: $BackupDir" -ForegroundColor Cyan
    Write-Host "   Will be created on first backup" -ForegroundColor Gray
}

Write-Host ""

# 6. Check backup scripts
Write-Host "6. Checking backup scripts..." -ForegroundColor Yellow
$scripts = @(
    "$ProjectPath\scripts\backup_to_gdrive.ps1",
    "$ProjectPath\scripts\schedule_gdrive_backup.ps1"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        $size = (Get-Item $script).Length
        Write-Host "   ✓ $(Split-Path $script -Leaf) ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $(Split-Path $script -Leaf) NOT found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Run manual backup test:" -ForegroundColor White
Write-Host "     powershell -ExecutionPolicy Bypass -File $ProjectPath\scripts\backup_to_gdrive.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. After successful backup, setup automation:" -ForegroundColor White
Write-Host "     powershell -ExecutionPolicy Bypass -File $ProjectPath\scripts\schedule_gdrive_backup.ps1" -ForegroundColor Gray
Write-Host ""
