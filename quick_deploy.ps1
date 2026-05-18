# Quick Start Deployment Script
# Usage: .\quick_deploy.ps1
# This script automates the complete deployment process

param(
    [string]$Environment = "development",
    [string]$PythonVersion = "3.11",
    [switch]$SkipBackup = $false,
    [switch]$Help = $false
)

# ============================================================================
# CONFIGURATION
# ============================================================================
$ProjectRoot = "C:\repos\proyek_manajemen_job"
$DataRoot = "C:\data\management-job"
$LogsRoot = "C:\logs\management-job"
$BackupRoot = "C:\backup\management-job"
$VenvPath = "$ProjectRoot\venv"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $color = $Colors[$Type]
    Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] $Message" -ForegroundColor $color
}

function Show-Help {
    Write-Host @"
Quick Deploy Script for Proyek Manajemen Job

USAGE:
    .\quick_deploy.ps1 [OPTIONS]

OPTIONS:
    -Environment <string>   : development, staging, or production (default: development)
    -PythonVersion <string> : Python version required (default: 3.11)
    -SkipBackup            : Skip database backup (use with caution)
    -Help                  : Show this help message

EXAMPLES:
    # Development deployment
    .\quick_deploy.ps1 -Environment development

    # Production deployment
    .\quick_deploy.ps1 -Environment production

    # Skip backup (for testing)
    .\quick_deploy.ps1 -Environment development -SkipBackup

REQUIREMENTS:
    - Python 3.11+ installed
    - PostgreSQL 16 running
    - Redis running
    - Virtual environment will be created if not exist
"@
}

function Test-Prerequisites {
    Write-Status "Checking prerequisites..." "Info"
    
    $prerequisitesFailed = $false
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "3\.11") {
            Write-Status "✓ Python 3.11 found: $pythonVersion" "Success"
        } else {
            Write-Status "✗ Python 3.11 not found (found: $pythonVersion)" "Error"
            $prerequisitesFailed = $true
        }
    } catch {
        Write-Status "✗ Python not installed or not in PATH" "Error"
        $prerequisitesFailed = $true
    }
    
    # Check PostgreSQL
    try {
        $pgVersion = psql --version 2>&1
        if ($pgVersion -match "16") {
            Write-Status "✓ PostgreSQL 16 found: $pgVersion" "Success"
        } else {
            Write-Status "⚠ PostgreSQL found but not version 16: $pgVersion" "Warning"
        }
    } catch {
        Write-Status "✗ PostgreSQL not installed or psql not in PATH" "Error"
        $prerequisitesFailed = $true
    }
    
    # Check Redis
    try {
        $redisTest = redis-cli ping 2>&1
        if ($redisTest -eq "PONG") {
            Write-Status "✓ Redis running and responding" "Success"
        } else {
            Write-Status "⚠ Redis ping failed: $redisTest" "Warning"
        }
    } catch {
        Write-Status "⚠ Redis not running or redis-cli not in PATH" "Warning"
    }
    
    return -not $prerequisitesFailed
}

function Create-Directories {
    Write-Status "Creating directory structure..." "Info"
    
    @($DataRoot, "$DataRoot\media", "$DataRoot\static", "$LogsRoot", "$BackupRoot") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Status "✓ Created: $_" "Success"
        } else {
            Write-Status "✓ Already exists: $_" "Success"
        }
    }
}

function Setup-VirtualEnvironment {
    Write-Status "Setting up Python virtual environment..." "Info"
    
    if (Test-Path $VenvPath) {
        Write-Status "✓ Virtual environment already exists" "Success"
    } else {
        Write-Status "Creating new virtual environment..." "Info"
        python -m venv $VenvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Status "✓ Virtual environment created" "Success"
        } else {
            Write-Status "✗ Failed to create virtual environment" "Error"
            return $false
        }
    }
    
    # Activate venv and upgrade pip
    Write-Status "Activating virtual environment and upgrading pip..." "Info"
    & "$VenvPath\Scripts\Activate.ps1"
    python -m pip install --upgrade pip setuptools wheel
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Pip upgraded" "Success"
    }
    
    return $true
}

function Install-Requirements {
    Write-Status "Installing Python requirements..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    pip install -r "$ProjectRoot\requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Requirements installed" "Success"
        return $true
    } else {
        Write-Status "✗ Failed to install requirements" "Error"
        return $false
    }
}

function Setup-Environment-File {
    Write-Status "Setting up environment configuration..." "Info"
    
    $envFile = "$ProjectRoot\.env"
    
    if (Test-Path $envFile) {
        Write-Status "✓ .env file already exists" "Success"
    } else {
        Write-Status "Creating .env from template..." "Info"
        Copy-Item "$ProjectRoot\.env.example" $envFile
        Write-Status "✓ .env file created from template" "Success"
        Write-Status "⚠ IMPORTANT: Edit .env with your actual values:" "Warning"
        Write-Status "   - SECRET_KEY (generate new one)" "Warning"
        Write-Status "   - DB_PASSWORD (your PostgreSQL password)" "Warning"
        Write-Status "   - DJANGO_PUBLIC_URL (your domain or IP)" "Warning"
    }
}

function Run-Django-Checks {
    Write-Status "Running Django system checks..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    
    if ($Environment -eq "production") {
        python manage.py check --deploy
    } else {
        python manage.py check
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Django system checks passed" "Success"
        return $true
    } else {
        Write-Status "✗ Django system checks failed" "Error"
        return $false
    }
}

function Backup-Database {
    if ($SkipBackup) {
        Write-Status "Skipping database backup (--SkipBackup flag set)" "Warning"
        return $true
    }
    
    Write-Status "Creating database backup..." "Info"
    
    $backupFile = "$BackupRoot\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    
    & "$VenvPath\Scripts\Activate.ps1"
    python manage.py dumpdata > $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        $backupSize = (Get-Item $backupFile).Length / 1MB
        Write-Status "✓ Backup created: $backupFile ($([Math]::Round($backupSize, 2)) MB)" "Success"
        return $true
    } else {
        Write-Status "✗ Backup failed" "Error"
        return $false
    }
}

function Run-Migrations {
    Write-Status "Applying database migrations..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    
    # First show migration plan
    Write-Status "Migration plan:" "Info"
    python manage.py migrate --plan
    
    # Then apply migrations
    Write-Status "Applying migrations..." "Info"
    python manage.py migrate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Migrations applied successfully" "Success"
        return $true
    } else {
        Write-Status "✗ Migration failed" "Error"
        return $false
    }
}

function Collect-Static-Files {
    Write-Status "Collecting static files..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    python manage.py collectstatic --noinput --clear
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Static files collected" "Success"
        return $true
    } else {
        Write-Status "✗ Failed to collect static files" "Error"
        return $false
    }
}

function Test-Application {
    Write-Status "Testing application..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    
    Write-Status "Starting development server for testing (Ctrl+C to stop)..." "Info"
    Write-Status "Access application at: http://localhost:8000" "Info"
    Write-Status "Admin panel at: http://localhost:8000/admin/" "Info"
    
    # Start server (user can stop with Ctrl+C)
    python manage.py runserver
}

function Generate-Secret-Key {
    Write-Status "Generating new SECRET_KEY..." "Info"
    
    & "$VenvPath\Scripts\Activate.ps1"
    
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    
    Write-Status "✓ Generated SECRET_KEY:" "Success"
    Write-Host "`n$secretKey`n"
    Write-Status "Add this to your .env file as: SECRET_KEY=$secretKey" "Info"
    
    return $secretKey
}

function Show-Post-Deployment-Steps {
    Write-Host @"

╔═══════════════════════════════════════════════════════════════════════════╗
║                    POST-DEPLOYMENT STEPS                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. EDIT CONFIGURATION
   - Edit .env with your actual values
   - Especially: SECRET_KEY, DB_PASSWORD, DJANGO_PUBLIC_URL
   
2. CREATE SUPERUSER (if not exists from restored database)
   - Run: python manage.py createsuperuser
   
3. TEST LOCALLY
   - Run: python manage.py runserver
   - Access: http://localhost:8000
   
4. SETUP PRODUCTION SERVICES
   - For PM2: Follow WINDOWS_SERVICE_PM2_SETUP.md
   - For Caddy reverse proxy: Setup Caddyfile
   
5. MONITORING
   - Check logs: C:\logs\management-job\
   - Monitor services: pm2 monit
   - Health check: .\health_check.ps1
   
6. BACKUPS
   - Setup automated daily backups
   - Test restore procedure
   - Store backups securely (off-site)

DOCUMENTATION:
   - DEPLOYMENT_CLEAN_SETUP.md       → Complete deployment guide
   - PORTS_SERVICES_REFERENCE.md     → Network configuration
   - WINDOWS_SERVICE_PM2_SETUP.md    → Service management with PM2
   - COMPATIBILITY_CHECKLIST.md      → Python 3.11 & PostgreSQL 16 info

"@
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Clear-Host
    
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════╗
║           PROYEK MANAJEMEN JOB - QUICK DEPLOYMENT SCRIPT                ║
║                  Windows Server 2022 Clean Setup                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

"@
    
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Status "Starting deployment with environment: $Environment" "Info"
    
    # Step 1: Test prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Status "Prerequisites check failed. Cannot proceed." "Error"
        return
    }
    
    # Step 2: Create directories
    Create-Directories
    
    # Step 3: Setup virtual environment
    if (-not (Setup-VirtualEnvironment)) {
        Write-Status "Virtual environment setup failed." "Error"
        return
    }
    
    # Step 4: Install requirements
    if (-not (Install-Requirements)) {
        Write-Status "Requirements installation failed." "Error"
        return
    }
    
    # Step 5: Setup environment file
    Setup-Environment-File
    
    # Step 6: Run Django checks
    if (-not (Run-Django-Checks)) {
        Write-Status "Django checks failed. Please review .env configuration." "Error"
        return
    }
    
    # Step 7: Backup database (if not skipped)
    if (-not (Backup-Database)) {
        Write-Status "Database backup failed. Proceeding anyway..." "Warning"
    }
    
    # Step 8: Run migrations
    if (-not (Run-Migrations)) {
        Write-Status "Migrations failed. Cannot proceed." "Error"
        return
    }
    
    # Step 9: Collect static files
    if (-not (Collect-Static-Files)) {
        Write-Status "Static files collection failed. Cannot proceed." "Error"
        return
    }
    
    Write-Status "═════════════════════════════════════════════════════════════" "Success"
    Write-Status "✓ DEPLOYMENT COMPLETE!" "Success"
    Write-Status "═════════════════════════════════════════════════════════════" "Success"
    
    # Show post-deployment steps
    Show-Post-Deployment-Steps
    
    # Ask if user wants to test application
    $response = Read-Host "`nDo you want to test the application locally? (y/n)"
    if ($response -eq "y") {
        Test-Application
    }
    
    # Optionally generate new SECRET_KEY
    $response = Read-Host "`nDo you want to generate a new SECRET_KEY? (y/n)"
    if ($response -eq "y") {
        $newKey = Generate-Secret-Key
    }
}

# ============================================================================
# EXECUTION
# ============================================================================

Main
