# 🪟 WINDOWS SERVICE SETUP - PM2 CONFIGURATION

## Prerequisites

- Node.js installed (for PM2) - https://nodejs.org/
- Python 3.11 virtual environment active
- PostgreSQL 16 running
- Redis running

---

## Installation

### Step 1: Install Node.js

```powershell
# Download and install Node.js (LTS version)
# From: https://nodejs.org/

# Verify installation
node --version
npm --version

# Should output: v18.x.x or later
```

### Step 2: Install PM2

```powershell
# Install PM2 globally
npm install -g pm2

# Verify installation
pm2 --version

# Should output: version number
```

### Step 3: Setup PM2 Ecosystem File

Create file: `C:\repos\proyek_manajemen_job\ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    {
      // Gunicorn WSGI Server
      name: 'gunicorn',
      script: '.\\run_gunicorn.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      exec_mode: 'cluster',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', 'logs', 'media', 'staticfiles'],
      max_memory_restart: '500M',
      
      // Error and output logs
      error_file: 'C:\\logs\\management-job\\pm2-gunicorn-error.log',
      out_file: 'C:\\logs\\management-job\\pm2-gunicorn-out.log',
      
      // Environment variables
      env: {
        DJANGO_ENVIRONMENT: 'production',
        NODE_ENV: 'production'
      },
      
      // Restart strategy
      max_restarts: 10,
      min_uptime: '30s',
      
      // Kill timeout (time to wait before force-kill)
      kill_timeout: 5000,
      listen_timeout: 10000
    },
    
    {
      // Celery Worker
      name: 'celery-worker',
      script: '.\\run_celery_worker.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', 'logs', 'media', 'staticfiles'],
      max_memory_restart: '1G',
      
      error_file: 'C:\\logs\\management-job\\pm2-celery-worker-error.log',
      out_file: 'C:\\logs\\management-job\\pm2-celery-worker-out.log',
      
      env: {
        DJANGO_ENVIRONMENT: 'production',
        NODE_ENV: 'production'
      },
      
      max_restarts: 10,
      min_uptime: '30s'
    },
    
    {
      // Celery Beat (Task Scheduler)
      name: 'celery-beat',
      script: '.\\run_celery_beat.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', 'logs', 'media', 'staticfiles'],
      max_memory_restart: '300M',
      
      error_file: 'C:\\logs\\management-job\\pm2-celery-beat-error.log',
      out_file: 'C:\\logs\\management-job\\pm2-celery-beat-out.log',
      
      env: {
        DJANGO_ENVIRONMENT: 'production',
        NODE_ENV: 'production'
      },
      
      max_restarts: 10,
      min_uptime: '30s'
    },
    
    {
      // Caddy Reverse Proxy
      name: 'caddy',
      script: 'C:\\caddy\\caddy.exe',
      args: 'run --config C:\\caddy\\Caddyfile',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '100M',
      
      error_file: 'C:\\logs\\management-job\\pm2-caddy-error.log',
      out_file: 'C:\\logs\\management-job\\pm2-caddy-out.log',
      
      env: {
        NODE_ENV: 'production'
      },
      
      max_restarts: 5,
      min_uptime: '30s'
    }
  ],
  
  // Global settings
  merge_logs: false,
  autorestart: true,
  max_memory_restart: '500M',
  
  // Environment variables for all apps
  env: {
    PYTHONUNBUFFERED: '1',
    DJANGO_SETTINGS_MODULE: 'config.settings_production'
  }
};
```

### Step 4: Create Batch Scripts

#### A. run_gunicorn.bat

Create: `C:\repos\proyek_manajemen_job\run_gunicorn.bat`

```batch
@echo off
setlocal enabledelayedexpansion

REM Change to project directory
cd /d C:\repos\proyek_manajemen_job

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set DJANGO_SETTINGS_MODULE=config.settings_production
set PYTHONUNBUFFERED=1

REM Run Gunicorn
gunicorn config.wsgi:application ^
  --workers 4 ^
  --worker-class sync ^
  --bind 127.0.0.1:8001 ^
  --timeout 60 ^
  --access-logfile C:\logs\management-job\gunicorn_access.log ^
  --error-logfile C:\logs\management-job\gunicorn_error.log ^
  --log-level info

REM Keep window open if error occurs
if errorlevel 1 (
  echo ERROR: Gunicorn failed to start
  pause
)
```

#### B. run_celery_worker.bat

Create: `C:\repos\proyek_manajemen_job\run_celery_worker.bat`

```batch
@echo off
setlocal enabledelayedexpansion

cd /d C:\repos\proyek_manajemen_job
call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=config.settings_production
set PYTHONUNBUFFERED=1

celery -A config worker ^
  --loglevel=info ^
  --concurrency=4 ^
  --logfile=C:\logs\management-job\celery_worker.log ^
  --pidfile=C:\logs\management-job\celery_worker.pid

if errorlevel 1 (
  echo ERROR: Celery worker failed to start
  pause
)
```

#### C. run_celery_beat.bat

Create: `C:\repos\proyek_manajemen_job\run_celery_beat.bat`

```batch
@echo off
setlocal enabledelayedexpansion

cd /d C:\repos\proyek_manajemen_job
call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=config.settings_production
set PYTHONUNBUFFERED=1

celery -A config beat ^
  --loglevel=info ^
  --scheduler django_celery_beat.schedulers:DatabaseScheduler ^
  --logfile=C:\logs\management-job\celery_beat.log ^
  --pidfile=C:\logs\management-job\celery_beat.pid

if errorlevel 1 (
  echo ERROR: Celery beat failed to start
  pause
)
```

---

## Starting Services

### Method 1: Start All Services at Once

```powershell
# Navigate to project directory
cd C:\repos\proyek_manajemen_job

# Start all services from ecosystem config
pm2 start ecosystem.config.js --name management-job

# Expected output:
# ┌─────┬────────────────┬─────────┬──────┬───────────┬──────────┐
# │ id  │ name           │ version │ mode │ status    │ restart  │
# ├─────┼────────────────┼─────────┼──────┼───────────┼──────────┤
# │ 0   │ gunicorn       │ N/A     │ fork │ online    │ 0        │
# │ 1   │ celery-worker  │ N/A     │ fork │ online    │ 0        │
# │ 2   │ celery-beat    │ N/A     │ fork │ online    │ 0        │
# │ 3   │ caddy          │ N/A     │ fork │ online    │ 0        │
# └─────┴────────────────┴─────────┴──────┴───────────┴──────────┘
```

### Method 2: Start Services Individually

```powershell
# Start Gunicorn only
pm2 start ecosystem.config.js --only gunicorn

# Start Celery worker only
pm2 start ecosystem.config.js --only celery-worker

# Start Celery beat only
pm2 start ecosystem.config.js --only celery-beat

# Start Caddy only
pm2 start ecosystem.config.js --only caddy
```

---

## Managing Services

### Check Status

```powershell
# List all PM2 processes
pm2 list

# Show detailed info
pm2 info gunicorn
pm2 info celery-worker

# Real-time monitoring
pm2 monit
```

### View Logs

```powershell
# Show all logs
pm2 logs

# Show specific service logs
pm2 logs gunicorn
pm2 logs celery-worker
pm2 logs celery-beat

# Follow logs in real-time
pm2 logs gunicorn --lines 50 --follow

# Clear logs
pm2 flush
```

### Restart Services

```powershell
# Restart specific service
pm2 restart gunicorn
pm2 restart celery-worker
pm2 restart celery-beat

# Restart all services
pm2 restart all

# Reload (zero-downtime restart)
pm2 reload gunicorn
```

### Stop Services

```powershell
# Stop specific service
pm2 stop gunicorn

# Stop all services
pm2 stop all
```

### Delete Services

```powershell
# Remove specific service
pm2 delete gunicorn

# Remove all services
pm2 delete all

# Or use save and kill
pm2 save
pm2 kill
```

---

## Auto-Start on Windows Reboot

### Option 1: PM2 Windows Startup

```powershell
# Save current PM2 configuration
pm2 save

# Create Windows service for PM2
pm2 install pm2-windows-startup

# This creates a Windows service that starts PM2 at boot
# You can verify in Services.msc - look for "PM2"
```

### Option 2: Task Scheduler

Create a scheduled task to start PM2 on Windows startup:

```powershell
# Run as Administrator

# Create task
$action = New-ScheduledTaskAction -Execute "pm2.cmd" -Argument "start ecosystem.config.js" -WorkingDirectory "C:\repos\proyek_manajemen_job"
$trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay "00:00:30"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "PM2-Management-Job" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Description "Start PM2 services for Proyek Manajemen Job"

# Verify task created
Get-ScheduledTask -TaskName "PM2-Management-Job" | Select-Object State, Author, Description
```

---

## Health Monitoring

### Health Check Script

```powershell
# File: health_check_pm2.ps1

Write-Host "=== PM2 HEALTH CHECK ===" -ForegroundColor Green

# 1. PM2 List
Write-Host "`n[1] PM2 Processes Status:"
pm2 list

# 2. Check individual service status
Write-Host "`n[2] Service Status Details:"
$services = @('gunicorn', 'celery-worker', 'celery-beat', 'caddy')
foreach ($service in $services) {
    $status = pm2 info $service | Select-String "status"
    Write-Host "  $service: $status" -ForegroundColor Green
}

# 3. Memory usage
Write-Host "`n[3] Memory Usage:"
pm2 monit --format json | ConvertFrom-Json | ForEach-Object {
    Write-Host "  $($_.name): $($_.memory / 1MB) MB" -ForegroundColor Green
}

# 4. Recent errors
Write-Host "`n[4] Recent Errors (last 10 lines):"
pm2 logs --err --lines 10

Write-Host "`n=== END HEALTH CHECK ===" -ForegroundColor Green
```

Run health check:
```powershell
.\health_check_pm2.ps1
```

---

## Troubleshooting

### Issue: Process keeps restarting

**Solution:**
```powershell
# 1. Check logs
pm2 logs gunicorn --lines 50

# 2. Verify environment variables in .env
cat .env | Select-String "DJANGO_ENVIRONMENT"

# 3. Check if port 8001 is available
netstat -ano | findstr :8001

# 4. Try running batch file manually to see error
.\run_gunicorn.bat
```

### Issue: Redis connection refused

**Solution:**
```powershell
# Verify Redis is running
Get-Service Redis-Service

# Check Redis is listening
redis-cli ping

# If not responding, restart Redis
Stop-Service Redis-Service
Start-Service Redis-Service

# Test connection again
redis-cli ping  # Should respond PONG
```

### Issue: PostgreSQL connection failed

**Solution:**
```powershell
# Check PostgreSQL service
Get-Service postgresql-x64-*

# Verify connection string in .env
# Run Django check
python manage.py check

# Test database directly
psql -U manajemen_app_user -d proyek_management_job -c "SELECT 1;"
```

### Issue: "Port 8001 already in use"

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <PID_NUMBER> /F

# Or change port in run_gunicorn.bat:
# --bind 127.0.0.1:8002

# And update Caddyfile to reverse proxy to 8002
```

---

## Performance Tuning

### Gunicorn Workers

Edit `run_gunicorn.bat`:
```batch
REM Number of workers = (2 × CPU cores) + 1
REM For 4-core CPU: use 9 workers
--workers 9

REM Or for 2-core CPU: use 5 workers
--workers 5
```

### Celery Workers

Edit `run_celery_worker.bat`:
```batch
REM Concurrency = number of CPU cores
celery -A config worker --concurrency=4

REM For high-load scenarios, use less concurrency for stability
celery -A config worker --concurrency=2 --pool=solo
```

### Memory Management

```powershell
# Monitor memory usage
pm2 monit

# If Celery worker uses too much memory, restart it
pm2 restart celery-worker

# Set memory limit in ecosystem.config.js:
# max_memory_restart: '1G'
```

---

## Backup & Disaster Recovery

### Save PM2 Configuration

```powershell
# Save current state
pm2 save

# This saves to:
# %APPDATA%\npm\node_modules\pm2\conf\dump.pm2

# For backup, also save ecosystem.config.js
Copy-Item C:\repos\proyek_manajemen_job\ecosystem.config.js `
  C:\backup\management-job\ecosystem.config.js.backup
```

### Restore PM2 Configuration

```powershell
# Restore saved configuration
pm2 resurrect

# Or manually start
pm2 start ecosystem.config.js
```

---

## Uninstallation (if needed)

```powershell
# Stop all services
pm2 stop all

# Delete all services
pm2 delete all

# Save configuration (for later recovery)
pm2 save

# Kill PM2 daemon
pm2 kill

# Uninstall PM2 globally
npm uninstall -g pm2
```

