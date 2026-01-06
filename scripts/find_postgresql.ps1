# Find PostgreSQL Installation
# ============================

Write-Host ""
Write-Host "Mencari PostgreSQL installation..." -ForegroundColor Yellow
Write-Host ""

# Check common PostgreSQL installation paths
$PossiblePaths = @(
    "C:\Program Files\PostgreSQL",
    "C:\Program Files (x86)\PostgreSQL",
    "C:\PostgreSQL"
)

$FoundPath = $null

foreach ($BasePath in $PossiblePaths) {
    if (Test-Path $BasePath) {
        Write-Host "Found: $BasePath" -ForegroundColor Green
        
        # List versions
        $Versions = Get-ChildItem $BasePath -Directory | Where-Object { $_.Name -match '^\d+' } | Sort-Object Name -Descending
        
        foreach ($Version in $Versions) {
            $BinPath = Join-Path $Version.FullName "bin"
            $PgDump = Join-Path $BinPath "pg_dump.exe"
            
            if (Test-Path $PgDump) {
                Write-Host "  Version $($Version.Name):" -ForegroundColor Cyan
                Write-Host "    pg_dump found: $PgDump" -ForegroundColor Green
                $FoundPath = $BinPath
                break
            }
        }
        
        if ($FoundPath) { break }
    }
}

if ($FoundPath) {
    Write-Host ""
    Write-Host "✓ PostgreSQL bin directory found:" -ForegroundColor Green
    Write-Host "  $FoundPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Update backup_to_gdrive.ps1 dengan path ini:" -ForegroundColor Yellow
    Write-Host '$env:Path += "';'' + $FoundPath' -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✗ PostgreSQL NOT found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solusi:" -ForegroundColor Yellow
    Write-Host "1. Install PostgreSQL Client tools dari: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host "2. Atau cek instalasi PostgreSQL di Control Panel > Programs" -ForegroundColor Gray
    Write-Host ""
}
