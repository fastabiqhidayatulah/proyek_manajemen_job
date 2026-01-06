# Simple Backup Script with Detailed Error Reporting
# ===================================================

$ProjectPath = "D:\proyek_management_job"
$BackupDir = "$ProjectPath\backups"
$PostgreSQLBin = "C:\Program Files\PostgreSQL\16\bin"
$RclonePath = "C:\Program Files\rclone\rclone.exe"
$LogFile = "$BackupDir\backup_log.txt"

# Add PostgreSQL to PATH
$env:Path += ";$PostgreSQLBin"

# Database config
$DBName = "proyek_management"
$DBUser = "postgres"
$DBHost = "localhost"
$DBPort = "5432"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP DATABASE TO GOOGLE DRIVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create backup directory
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "✓ Backup directory created: $BackupDir" -ForegroundColor Green
}

# Generate filename
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BackupFile = "$BackupDir\backup_${DBName}_${Timestamp}.sql"
$CompressedFile = "$BackupFile.gz"

Write-Host "✓ Backup file: $BackupFile" -ForegroundColor Green
Write-Host ""

# Step 1: Dump database
Write-Host "Step 1: Dumping database '$DBName'..." -ForegroundColor Yellow
Write-Host "Command: pg_dump -h $DBHost -U $DBUser -d $DBName -f $BackupFile" -ForegroundColor Gray
Write-Host ""

$BackupOutput = pg_dump -h $DBHost -U $DBUser -d $DBName -f $BackupFile 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database dump failed!" -ForegroundColor Red
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $BackupOutput -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Check if PostgreSQL service is running" -ForegroundColor Gray
    Write-Host "   - Open Services: services.msc" -ForegroundColor Gray
    Write-Host "   - Look for 'postgresql-x64-16'" -ForegroundColor Gray
    Write-Host "2. Check database credentials" -ForegroundColor Gray
    Write-Host "   - User: $DBUser" -ForegroundColor Gray
    Write-Host "   - Database: $DBName" -ForegroundColor Gray
    Write-Host "   - Host: $DBHost" -ForegroundColor Gray
    Write-Host "   - Port: $DBPort" -ForegroundColor Gray
    Write-Host "3. Check if database exists:" -ForegroundColor Gray
    Write-Host "   - psql -U postgres -l" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

$FileSize = (Get-Item $BackupFile).Length / 1MB
Write-Host "✓ Database dumped successfully! Size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Green
Write-Host ""

# Step 2: Compress
Write-Host "Step 2: Compressing backup file..." -ForegroundColor Yellow
try {
    Compress-Archive -Path $BackupFile -DestinationPath $CompressedFile -Force
    Remove-Item $BackupFile -Force
    
    $CompressedSize = (Get-Item $CompressedFile).Length / 1MB
    Write-Host "✓ Compressed successfully! Size: $([math]::Round($CompressedSize, 2)) MB" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Compression failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Upload to Google Drive
Write-Host "Step 3: Uploading to Google Drive..." -ForegroundColor Yellow
Write-Host "Command: rclone copy '$CompressedFile' 'gdrive:/proyek_management_backup/'" -ForegroundColor Gray
Write-Host ""

$UploadOutput = cmd /c $RclonePath copy $CompressedFile "gdrive:/proyek_management_backup/" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Upload failed!" -ForegroundColor Red
    Write-Host "Details:" -ForegroundColor Red
    Write-Host $UploadOutput -ForegroundColor Red
    exit 1
}

Write-Host "✓ Upload completed successfully!" -ForegroundColor Green
Write-Host ""

# Success message
Write-Host "========================================" -ForegroundColor Green
Write-Host "BACKUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Database: $DBName" -ForegroundColor Gray
Write-Host "  Backup file: $(Split-Path $CompressedFile -Leaf)" -ForegroundColor Gray
Write-Host "  Size: $([math]::Round($CompressedSize, 2)) MB" -ForegroundColor Gray
Write-Host "  Location: gdrive:/proyek_management_backup/" -ForegroundColor Gray
Write-Host ""
