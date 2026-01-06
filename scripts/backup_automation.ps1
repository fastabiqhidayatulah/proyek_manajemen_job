# Backup Database to Google Drive - Automation Script
# ====================================================

$RclonePath = "C:\Program Files\rclone\rclone.exe"
$PostgreSQLBin = "C:\Program Files\PostgreSQL\16\bin"
$BackupDir = "D:\proyek_management_job\backups"
$LogFile = "$BackupDir\backup_log.txt"

# Database config
$DBName = "manajemen_pekerjaan_db"
$DBUser = "manajemen_app_user"
$DBPassword = "AppsPassword123!"
$DBHost = "localhost"
$DBPort = "5432"

# Add PostgreSQL to PATH
$env:Path += ";$PostgreSQLBin"

# ================================================
# FUNCTIONS
# ================================================

function Log-Message {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Create-Backup-File {
    $Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    return "$BackupDir\backup_${DBName}_${Timestamp}.sql"
}

# ================================================
# MAIN SCRIPT
# ================================================

# Create backup directory
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Log-Message "Created backup directory: $BackupDir"
}

Log-Message "========== BACKUP STARTED =========="

# Generate backup filename
$BackupFile = Create-Backup-File
Log-Message "Backup file: $BackupFile"

# Step 1: Dump database
Log-Message "Step 1: Dumping database..."
$env:PGPASSWORD = $DBPassword
pg_dump -h $DBHost -U $DBUser -d $DBName -f $BackupFile 2>&1 | ForEach-Object { Log-Message $_ }

if ($LASTEXITCODE -ne 0) {
    Log-Message "ERROR: Database dump failed!"
    exit 1
}

$FileSize = (Get-Item $BackupFile).Length / 1MB
Log-Message "SUCCESS: Database dumped! Size: $([math]::Round($FileSize, 2)) MB"

# Step 2: Upload to Google Drive
Log-Message "Step 2: Uploading to Google Drive..."
& $RclonePath copy $BackupFile "gdrive:/proyek_management_backup/" -v 2>&1 | ForEach-Object { Log-Message $_ }

if ($LASTEXITCODE -ne 0) {
    Log-Message "ERROR: Upload to Google Drive failed!"
    exit 1
}

Log-Message "SUCCESS: Uploaded to Google Drive!"

# Step 3: Cleanup old backups (keep last 7 days)
Log-Message "Step 3: Cleaning up old backups..."
$CutoffDate = (Get-Date).AddDays(-7)
$OldBackups = Get-ChildItem $BackupDir -Filter "backup_${DBName}_*.sql" | Where-Object { $_.LastWriteTime -lt $CutoffDate }

if ($OldBackups.Count -gt 0) {
    foreach ($OldBackup in $OldBackups) {
        Remove-Item $OldBackup.FullName -Force
        Log-Message "Deleted old backup: $($OldBackup.Name)"
    }
    Log-Message "Cleanup completed: $($OldBackups.Count) old backup(s) removed"
} else {
    Log-Message "No old backups to remove"
}

Log-Message "========== BACKUP COMPLETED =========="
Log-Message ""

Write-Host "Backup completed successfully!"
Write-Host "Log: $LogFile"
