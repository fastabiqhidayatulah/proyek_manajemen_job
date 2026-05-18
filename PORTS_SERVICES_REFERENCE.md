# 📋 PORT & SERVICE USAGE REFERENCE

## Network Ports

### Application Ports

| Service | Port | Protocol | Purpose | Status |
|---------|------|----------|---------|--------|
| Django Dev | 8000 | HTTP | Local development server | Development only |
| Django Prod | 8001 | HTTP | Gunicorn WSGI server | Production |
| PostgreSQL | 5432 | TCP | Database connection | Required |
| Redis | 6379 | TCP | Celery broker & cache | Required |
| Caddy | 80 | HTTP | Reverse proxy (HTTP) | Production |
| Caddy | 443 | HTTPS | Reverse proxy (HTTPS) | Production (optional) |
| Admin Panel | 8000/admin | HTTP | Django admin interface | All environments |

### Usage Verification

```powershell
# Check if port is in use (PowerShell)
netstat -ano | findstr :PORT_NUMBER

# Example: Check port 5432 (PostgreSQL)
netstat -ano | findstr :5432

# Kill process using port (if needed)
taskkill /PID PID_NUMBER /F

# Check service status
Get-Service | Where-Object {$_.Name -match 'postgres|redis'} | Select-Object Status, Name
```

---

## Windows Services/Processes

### Required Services

| Service | Name | Type | Auto-start | Status |
|---------|------|------|-----------|--------|
| PostgreSQL | postgresql-x64-16 | Windows Service | ✓ Enabled | Critical |
| Redis | Redis-Service | Windows Service | ✓ Enabled | Critical |
| Gunicorn | N/A | Python Process / PM2 | ✓ PM2 managed | Critical |
| Celery Worker | N/A | Python Process / PM2 | ✓ PM2 managed | Important |
| Celery Beat | N/A | Python Process / PM2 | ✓ PM2 managed | Important |
| Caddy | N/A | Windows Service / PM2 | ✓ PM2 managed | Important |

### Service Management

```powershell
# PostgreSQL
Start-Service postgresql-x64-16
Stop-Service postgresql-x64-16
Restart-Service postgresql-x64-16
Get-Service postgresql-x64-16

# Redis (if installed as service)
Start-Service Redis
Stop-Service Redis

# PM2 Services (Node-based service management)
pm2 start ecosystem.config.js
pm2 stop all
pm2 restart all
pm2 monit
pm2 logs
pm2 save
pm2 startup

# Check all Python processes
Get-Process python | Select-Object ProcessName, Id, Memory
```

---

## Network Configuration

### Firewall Rules (Windows Firewall)

```powershell
# Allow PostgreSQL
New-NetFirewallRule -DisplayName "Allow PostgreSQL" `
  -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow

# Allow Redis
New-NetFirewallRule -DisplayName "Allow Redis" `
  -Direction Inbound -LocalPort 6379 -Protocol TCP -Action Allow

# Allow HTTP (Caddy)
New-NetFirewallRule -DisplayName "Allow HTTP" `
  -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Allow HTTPS (Caddy)
New-NetFirewallRule -DisplayName "Allow HTTPS" `
  -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# Allow SSH (if using VS Code Remote SSH)
New-NetFirewallRule -DisplayName "Allow SSH" `
  -Direction Inbound -LocalPort 22 -Protocol TCP -Action Allow

# List all rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -match 'Management-Job|Django|Celery'} | Select-Object DisplayName, Direction, Action
```

---

## Environmental Service Ports Map

### Development Environment (Local VM)

```
Internet
  │
  └─→ VS Code Remote SSH (Port 22)
        │
        └─→ Django Dev Server (0.0.0.0:8000)
              ├─→ PostgreSQL (localhost:5432)
              ├─→ Redis (localhost:6379)
              └─→ Media Files (file:// protocol)
```

### Production Environment (Windows Server 2022)

```
Internet (HTTPS)
  │
  └─→ Caddy Reverse Proxy (0.0.0.0:443)
        │
        └─→ HTTP Backend (127.0.0.1:8001)
              ├─→ Gunicorn WSGI (127.0.0.1:8001)
              │     └─→ Django Application
              ├─→ PostgreSQL (localhost:5432)
              ├─→ Redis (localhost:6379)
              │     ├─→ Celery Broker (6379/0)
              │     ├─→ Celery Result Backend (6379/0)
              │     └─→ Cache Backend (6379/1)
              └─→ Static Files (C:\data\management-job\static)

PM2 Process Manager (Node.js)
  ├─→ gunicorn process
  ├─→ celery worker processes
  ├─→ celery beat scheduler
  └─→ caddy process
```

---

## Connection Strings Reference

### PostgreSQL

```
Development:
  psql -U manajemen_app_user -d proyek_management_job -h localhost -p 5432

Production (.env):
  DB_ENGINE=django.db.backends.postgresql
  DB_NAME=proyek_management_job
  DB_USER=manajemen_app_user
  DB_PASSWORD=<strong-password>
  DB_HOST=localhost
  DB_PORT=5432
```

### Redis

```
Development & Production:
  redis-cli -h localhost -p 6379

Health check:
  redis-cli ping

Select database:
  redis-cli -n 0  # Celery broker/result
  redis-cli -n 1  # Cache backend
```

### Django Admin

```
Development: http://localhost:8000/admin/
Production: https://yourdomain.com/admin/
Behind Caddy: https://yourdomain.com/admin/
```

---

## Monitoring & Health Checks

### Quick Health Check Script

```powershell
# File: health_check.ps1

Write-Host "=== PROYEK MANAJEMEN JOB - HEALTH CHECK ===" -ForegroundColor Green

# 1. Check PostgreSQL
Write-Host "`n[1] PostgreSQL Status:"
$pgService = Get-Service postgresql-x64-16 -ErrorAction SilentlyContinue
if ($pgService.Status -eq "Running") {
    Write-Host "✓ PostgreSQL service running" -ForegroundColor Green
} else {
    Write-Host "✗ PostgreSQL service not running" -ForegroundColor Red
}

# 2. Check Redis
Write-Host "`n[2] Redis Status:"
$redisCheck = redis-cli ping 2>$null
if ($redisCheck -eq "PONG") {
    Write-Host "✓ Redis responding" -ForegroundColor Green
} else {
    Write-Host "✗ Redis not responding" -ForegroundColor Red
}

# 3. Check Django Application
Write-Host "`n[3] Django Application:"
$djangoCheck = Invoke-WebRequest -Uri "http://localhost:8001/admin/" -ErrorAction SilentlyContinue
if ($djangoCheck.StatusCode -eq 200) {
    Write-Host "✓ Django application responding" -ForegroundColor Green
} else {
    Write-Host "✗ Django application not responding" -ForegroundColor Red
}

# 4. Check Celery Worker
Write-Host "`n[4] Celery Worker Status:"
$celeryCheck = celery -A config inspect active 2>$null
if ($?) {
    Write-Host "✓ Celery worker active" -ForegroundColor Green
} else {
    Write-Host "✗ Celery worker not running" -ForegroundColor Red
}

# 5. Check PM2 Processes
Write-Host "`n[5] PM2 Managed Processes:"
pm2 list

Write-Host "`n=== END HEALTH CHECK ===" -ForegroundColor Green
```

---

## Troubleshooting Port Conflicts

### If Port is Already in Use

```powershell
# Find what's using the port
netstat -ano | findstr :8001

# Example output:
# TCP    127.0.0.1:8001    0.0.0.0:0    LISTENING    12345

# Kill the process
taskkill /PID 12345 /F

# Or find by name
Get-Process | Where-Object {$_.Id -eq 12345} | Stop-Process -Force

# Or find by port using netsh
netsh int ipv4 show tcpconnections | findstr :8001
```

### Port Binding Options

```powershell
# Change Gunicorn port in run_gunicorn.bat
gunicorn config.wsgi:application --bind 127.0.0.1:8002  # Use port 8002 instead

# Change Caddy listen port in Caddyfile
:8080 {
    reverse_proxy 127.0.0.1:8002
}

# Change Redis port
redis-server --port 6380
```

---

## Performance Monitoring

### Monitor Active Connections

```powershell
# PostgreSQL connections
psql -U manajemen_app_user -d proyek_management_job -c "SELECT pid, usename, state FROM pg_stat_activity;"

# Redis info
redis-cli info stats
redis-cli info memory
redis-cli dbsize

# System resources
Get-Process | Where-Object {$_.ProcessName -match 'python|postgres|redis'} | Select-Object ProcessName, CPU, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet / 1MB, 2)}}

# Network connections
netstat -ano | grep ESTABLISHED | Measure-Object
```

---

## Maintenance Tasks

### Daily

- [ ] Monitor health check output
- [ ] Check error logs: `C:\logs\management-job\errors.log`
- [ ] Check Celery tasks: `celery -A config inspect active`

### Weekly

- [ ] Restart services (off-peak hours)
- [ ] Clean old log files (>30 days)
- [ ] Run database optimization: `VACUUM ANALYZE;`

### Monthly

- [ ] Database backup verification
- [ ] Performance analysis (slow queries)
- [ ] Security updates check

