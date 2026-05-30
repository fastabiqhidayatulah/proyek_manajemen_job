# ⚡ QUICK START GUIDE - Sistem Manajemen Pekerjaan

**Untuk startup cepat dan troubleshooting emergency**

---

## 🚀 **Startup (First Time)**

```powershell
cd C:\repos\proyek_manajemen_job

# 1. Activate venv
.\venv\Scripts\Activate.ps1

# 2. Start all PM2 apps
pm2 start ecosystem.config.js

# 3. Verify running
pm2 status
```

**Expected output:**
```
✅ management-django        online
✅ management-celery-worker online
✅ management-celery-beat   online
```

---

## 🌐 **Access Application**

| Purpose | URL |
|---------|-----|
| **Main App** | http://192.168.111.130:4321 |
| **Admin Panel** | http://192.168.111.130:4321/admin/ |
| **Leave/Cuti** | http://192.168.111.130:4321/leave/ |
| **Dashboard** | http://192.168.111.130:4321/dashboard/ |

**Login:** admin / admin123

---

## 🎛️ **Service Management**

### **Start**
```powershell
pm2 start management-django              # Start Django only
pm2 start all                            # Start all
pm2 start ecosystem.config.js            # From config file
```

### **Stop**
```powershell
pm2 stop management-django               # Stop specific
pm2 stop all                             # Stop all
```

### **Restart**
```powershell
pm2 restart management-django
pm2 restart all
```

### **Status**
```powershell
pm2 status                   # Table format
pm2 logs                     # View logs
pm2 monit                    # Real-time monitoring
```

---

## 📊 **Monitor Logs**

```powershell
# All logs
pm2 logs

# Specific app
pm2 logs management-django --lines 100
pm2 logs management-celery-worker --lines 50

# Real-time
pm2 logs management-django --lines 0 --follow

# Clear logs
pm2 flush
```

---

## 🔍 **Health Check**

```powershell
# Web server
(Invoke-WebRequest -Uri "http://127.0.0.1:4321/" -UseBasicParsing).StatusCode
# Expected: 302 or 200

# Database
psql -U postgres -d proyek_management_job -c "SELECT 1;"
# Expected: 1 row

# Redis
redis-cli -p 6379 ping
# Expected: PONG

# Celery
python manage.py shell
>>> from celery.app.control import Inspect
>>> i = Inspect()
>>> i.active()
```

---

## ⚠️ **Emergency Restart**

```powershell
# 1. Kill all
pm2 kill

# 2. Wait 2 seconds
Start-Sleep -Seconds 2

# 3. Start fresh
pm2 start ecosystem.config.js

# 4. Verify
pm2 status
```

---

## 🆘 **Troubleshooting**

### **Django won't start**

```powershell
# Check what's using port 4321
netstat -ano | findstr :4321

# Kill it
taskkill /PID <number> /F

# Restart
pm2 restart management-django
```

### **Database unreachable**

```powershell
# Check PostgreSQL service
Get-Service PostgreSQL*

# Connect manually to verify
psql -U postgres
> \l   # List databases
> \q   # Quit

# Restart if needed
Restart-Service PostgreSQL-x64-16
```

### **Celery not processing**

```powershell
# Restart worker
pm2 restart management-celery-worker

# Check Redis
redis-cli
> DBSIZE
> FLUSHDB  # Clear queue if stuck
> EXIT

# Check tasks
python manage.py celery purge
pm2 restart management-celery-beat
```

### **High CPU/Memory**

```powershell
# Check which process
pm2 status  # Look at CPU/memory columns

# Restart specific process
pm2 restart management-django  # Or whichever

# Check logs for errors
pm2 logs management-celery-worker --lines 200
```

---

## 📁 **Important Directories**

```
Application:     C:\repos\proyek_manajemen_job
Logs:            C:\logs\management-job
Media:           C:\data\management-job\media
Backups:         C:\repos\proyek_manajemen_job\backups
Virtual env:     C:\repos\proyek_manajemen_job\venv
```

---

## 💾 **Backup Database**

```powershell
# Backup
pg_dump -U postgres proyek_management_job > backups/backup_$(Get-Date -Format yyyy-MM-dd_HHmmss).sql

# Restore (⚠️ WARNING: This will overwrite!)
psql -U postgres -d proyek_management_job < backups/backup_2026-05-26.sql
```

---

## 🔧 **Config Files**

```
.env              → Environment variables (DO NOT COMMIT)
ecosystem.config.js → PM2 configuration
config/settings.py  → Django settings
```

---

## 📞 **Support Files**

```
SETUP_PM2_DOKUMENTASI.md  → Detailed setup guide
KONFIGURASI_RINGKAS.md    → Quick reference
QUICK_START.md (this file) → Emergency procedures
```

---

**Last updated:** 30 Mei 2026
