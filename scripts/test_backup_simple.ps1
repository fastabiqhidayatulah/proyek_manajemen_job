# Ultra Simple Backup Test
# =======================

$RclonePath = "C:\Program Files\rclone\rclone.exe"

Write-Host ""
Write-Host "==== BACKUP TEST ===="
Write-Host ""

# 1. Check if rclone exists
Write-Host "1. Checking rclone..." -ForegroundColor Yellow
if (Test-Path $RclonePath) {
    Write-Host "   OK - rclone found" -ForegroundColor Green
} else {
    Write-Host "   ERROR - rclone not found at: $RclonePath" -ForegroundColor Red
    exit 1
}

# 2. Test rclone version
Write-Host ""
Write-Host "2. Rclone version:" -ForegroundColor Yellow
cmd /c $RclonePath --version

# 3. List remotes
Write-Host ""
Write-Host "3. Rclone remotes:" -ForegroundColor Yellow
cmd /c $RclonePath listremotes

# 4. Test Google Drive connection
Write-Host ""
Write-Host "4. Testing Google Drive..." -ForegroundColor Yellow
cmd /c $RclonePath lsd gdrive:/

# 5. List backup folder
Write-Host ""
Write-Host "5. Backup folder in Google Drive:" -ForegroundColor Yellow
cmd /c $RclonePath ls gdrive:/proyek_management_backup

Write-Host ""
Write-Host "==== TEST COMPLETE ===="
Write-Host ""
