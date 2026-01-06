# Backup Database to Google Drive using rclone
# ================================================
# Script: backup_to_gdrive.ps1
# Usage: powershell -ExecutionPolicy Bypass -File "C:\path\to\backup_to_gdrive.ps1"
# Or schedule via Windows Task Scheduler

# Configuration
$ProjectPath = "D:\proyek_management_job"
$BackupDir = "$ProjectPath\backups"
$RclonePath = "C:\Program Files\rclone\rclone.exe"
$PostgreSQLBin = "C:\Program Files\PostgreSQL\16\bin"
$RemoteName = "gdrive"
$RemoteFolder = "proyek_management_backup"  # Folder di Google Drive
$LogFile = "$BackupDir\backup_log.txt"
$DBName = "proyek_management"
$DBUser = "postgres"
$DBHost = "localhost"
$DBPort = "5432"

# Add PostgreSQL to PATH
$env:Path += ";$PostgreSQLBin"

# ================================================
# 1. CREATE BACKUP DIRECTORY IF NOT EXISTS
# ================================================
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Backup directory created: $BackupDir"
}

# ================================================
# 2. GENERATE BACKUP FILENAME WITH TIMESTAMP
# ================================================
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BackupFile = "$BackupDir\backup_${DBName}_${Timestamp}.sql"
$CompressedFile = "$BackupFile.gz"

# ================================================
# 3. DUMP DATABASE
# ================================================
Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Starting database backup..."

try {
    # Set PostgreSQL password environment variable (if needed)
    # $env:PGPASSWORD = "your_password"
    
    # Run pg_dump
    & pg_dump --host=$DBHost --port=$DBPort --username=$DBUser --db=$DBName > $BackupFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Database backup completed: $BackupFile"
    } else {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR: Database backup failed!"
        exit 1
    }
}
catch {
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR: $_"
    exit 1
}

# ================================================
# 4. COMPRESS BACKUP FILE
# ================================================
Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Compressing backup file..."

try {
    # Compress using PowerShell (requires .NET)
    Compress-Archive -Path $BackupFile -DestinationPath $CompressedFile -Force
    
    # Remove original uncompressed file
    Remove-Item $BackupFile -Force
    
    $FileSize = (Get-Item $CompressedFile).Length / 1MB
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Compressed file created: $CompressedFile (Size: $([math]::Round($FileSize, 2)) MB)"
}
catch {
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR during compression: $_"
    exit 1
}

# ================================================
# 5. UPLOAD TO GOOGLE DRIVE USING RCLONE
# ================================================
Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Uploading to Google Drive..."

try {
    # Upload using rclone
    & $RclonePath copy $CompressedFile "${RemoteName}:${RemoteFolder}/" --progress
    
    if ($LASTEXITCODE -eq 0) {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Upload to Google Drive completed successfully!"
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Remote path: ${RemoteName}:${RemoteFolder}/"
    } else {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR: Upload to Google Drive failed!"
        exit 1
    }
}
catch {
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR during upload: $_"
    exit 1
}

# ================================================
# 6. CLEANUP OLD BACKUPS (KEEP LAST 7 DAYS)
# ================================================
Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Cleaning up old backups..."

try {
    $CutoffDate = (Get-Date).AddDays(-7)
    $OldBackups = Get-ChildItem $BackupDir -Filter "backup_${DBName}_*.gz" | Where-Object { $_.LastWriteTime -lt $CutoffDate }
    
    foreach ($OldBackup in $OldBackups) {
        Remove-Item $OldBackup.FullName -Force
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Deleted old backup: $($OldBackup.Name)"
    }
    
    if ($OldBackups.Count -gt 0) {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Cleanup completed: $($OldBackups.Count) old backup(s) removed"
    } else {
        Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - No old backups to remove"
    }
}
catch {
    Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - WARNING: Cleanup failed: $_"
}

# ================================================
# 7. FINAL STATUS
# ================================================
Add-Content $LogFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ===== BACKUP PROCESS COMPLETED SUCCESSFULLY ====="
Add-Content $LogFile ""

Write-Host "Backup selesai! Cek log di: $LogFile"
Write-Host "File backup: $(Split-Path $CompressedFile -Leaf)"
Write-Host "Tersimpan di Google Drive: $RemoteFolder"
